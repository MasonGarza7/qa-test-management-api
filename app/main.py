from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError

from app.db.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut

from app.models.test_case import TestCase
from app.schemas.test_case import TestCaseCreate, TestCaseOut
from app.schemas.test_case import TestCaseUpdate

from app.models.test_run import TestRun
from app.schemas.test_run import TestRunCreate, TestRunOut

from app.models.test_result import TestResult
from app.schemas.test_result import TestResultCreate, TestResultOut

from app.schemas.report import TestRunReportOut, TestRunInfo, TestResultLine

from app.schemas.coverage import TestRunCoverageOut, CoverageLine

from app.schemas.history import TestCaseHistoryOut, TestCaseHistoryLine



app = FastAPI(title="QA Test Management API")


@app.get("/")
def root():
    return {"status": "ok", "message": "QA Test Management API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/health/db")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}



# ------------------ USERS ------------------
@app.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(email=payload.email, name=payload.name, role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



# ------------------ PROJECTS ------------------
@app.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()




# ------------------ TEST CASES ------------------
@app.post("/test-cases", response_model=TestCaseOut, status_code=201)
def create_test_case(payload: TestCaseCreate, db: Session = Depends(get_db)):
    test_case = TestCase(**payload.model_dump())
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@app.get("/test-cases", response_model=list[TestCaseOut])
def list_test_cases(db: Session = Depends(get_db)):
    return db.query(TestCase).all()


@app.delete("/test-cases/{test_case_id}", status_code=204)
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()

    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    db.delete(test_case)
    db.commit()
    return


@app.put("/test-cases/{test_case_id}", response_model=TestCaseOut)
def update_test_case(
    test_case_id: int,
    payload: TestCaseUpdate,
    db: Session = Depends(get_db),
):
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()

    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(test_case, key, value)

    db.commit()
    db.refresh(test_case)
    return test_case



# ------------------ TEST RUNS ------------------
@app.post("/test-runs", response_model=TestRunOut, status_code=201)
def create_test_run(payload: TestRunCreate, db: Session = Depends(get_db)):
    test_run = TestRun(**payload.model_dump())
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    return test_run


@app.get("/test-runs", response_model=list[TestRunOut])
def list_test_runs(db: Session = Depends(get_db)):
    return db.query(TestRun).all()



# ------------------ TEST RESULTS ------------------
@app.post("/test-results", response_model=TestResultOut, status_code=201)
def create_test_result(payload: TestResultCreate, db: Session = Depends(get_db)):
    try:
        result = TestResult(**payload.model_dump())
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This test case already has a result for this test run."
        )
    except DataError:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Invalid status value."
        )



@app.get("/test-results", response_model=list[TestResultOut])
def list_test_results(db: Session = Depends(get_db)):
    return db.query(TestResult).all()



# ------------------ TEST REPORTS ------------------
@app.get("/test-runs/{run_id}/report", response_model=TestRunReportOut)
def get_test_run_report(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()

    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")

    # Build result lines (includes test case titles via ORM relationship)
    lines: list[TestResultLine] = []
    for r in run.results:
        lines.append(
            TestResultLine(
                id=r.id,
                test_case_id=r.test_case_id,
                test_case_title=r.test_case.title,
                status=r.status,
                notes=r.notes,
                created_at=r.created_at,
            )
        )

    return TestRunReportOut(run=run, results=lines)



# ------------------ TEST COVERAGE ------------------
@app.get("/test-runs/{run_id}/coverage", response_model=TestRunCoverageOut)
def get_test_run_coverage(run_id: int, db: Session = Depends(get_db)):
    run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")

    # All test cases for the project
    test_cases = db.query(TestCase).filter(TestCase.project_id == run.project_id).all()

    # All results for this run, keyed by test_case_id
    results = db.query(TestResult).filter(TestResult.test_run_id == run_id).all()
    results_by_case_id = {r.test_case_id: r for r in results}

    lines: list[CoverageLine] = []
    executed = 0
    pass_count = 0
    fail_count = 0
    blocked_count = 0
    skipped_count = 0


    for tc in test_cases:
        r = results_by_case_id.get(tc.id)
        if r:
            executed += 1
            if r.status == "pass":
                pass_count += 1
            elif r.status == "fail":
                fail_count += 1
            elif r.status == "blocked":
                blocked_count += 1
            elif r.status == "skipped":
                skipped_count += 1

            lines.append(
                CoverageLine(
                    test_case_id=tc.id,
                    title=tc.title,
                    status=r.status,
                    notes=r.notes,
                )
            )
        else:
            lines.append(
                CoverageLine(
                    test_case_id=tc.id,
                    title=tc.title,
                    status="not_run",
                    notes=None,
                )
            )

    total = len(test_cases)
    not_run = total - executed
    pass_rate = None
    if executed > 0:
        pass_rate = pass_count / executed


    return TestRunCoverageOut(
        run_id=run_id,
        project_id=run.project_id,
        total_cases=total,
        executed_cases=executed,
        not_run_cases=not_run,
        lines=lines,
        pass_count=pass_count,
        fail_count=fail_count,
        blocked_count=blocked_count,
        skipped_count=skipped_count,
        pass_rate=pass_rate,
    )



# ------------------ TEST CASE HISTORY ------------------
@app.get("/test-cases/{test_case_id}/history", response_model=TestCaseHistoryOut)
def get_test_case_history(test_case_id: int, db: Session = Depends(get_db)):
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    results = (
        db.query(TestResult)
        .filter(TestResult.test_case_id == test_case_id)
        .order_by(TestResult.created_at.desc())
        .all()
    )

    lines: list[TestCaseHistoryLine] = []
    for r in results:
        # r.test_run may be lazily loaded; SQLAlchemy will fetch it when accessed
        run = r.test_run
        lines.append(
            TestCaseHistoryLine(
                run_id=run.id,
                run_name=run.name,
                environment=run.environment,
                status=r.status,
                notes=r.notes,
                created_at=r.created_at,
            )
        )

    return TestCaseHistoryOut(
        test_case_id=test_case.id,
        title=test_case.title,
        history=lines,
    )
