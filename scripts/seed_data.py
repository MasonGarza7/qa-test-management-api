import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User, Project, TestCase, TestRun, TestResult

from dotenv import load_dotenv


load_dotenv()


def main() -> None:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set. Check your .env and restart the terminal.")

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with SessionLocal() as db:
        # Project (re-use if exists)
        project = db.query(Project).filter(Project.name == "Enterprise Portal 3.0").first()
        if not project:
            project = Project(name="Enterprise Portal 3.0", description="Major release testing")
            db.add(project)
            db.commit()
            db.refresh(project)

        # User (re-use if exists)
        user = db.query(User).filter(User.email == "mason@example.com").first()
        if not user:
            user = User(email="mason@example.com", name="Mason Garza", role="qa", project_id=project.id)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Test cases (only add if none exist for the project)
        if db.query(TestCase).filter(TestCase.project_id == project.id).count() == 0:
            db.add_all(
                [
                    TestCase(project_id=project.id, title="Login accepts valid credentials", description="Happy path login", priority="high"),
                    TestCase(project_id=project.id, title="Invalid password rejected", description="Negative login", priority="high"),
                    TestCase(project_id=project.id, title="Password reset email sent", description="Reset flow", priority="medium"),
                    TestCase(project_id=project.id, title="User can logout", description="Session termination", priority="low"),
                ]
            )
            db.commit()

        cases = (
            db.query(TestCase)
            .filter(TestCase.project_id == project.id)
            .order_by(TestCase.id)
            .all()
        )

        # New run each time (so history endpoints are interesting)
        run = TestRun(
            project_id=project.id,
            executed_by_user_id=user.id,
            name="Regression Run - Seed Data 2",
            environment="staging",
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        # Results for first 4 cases (if available)
        seed_pairs = []
        if len(cases) >= 1:
            seed_pairs.append((cases[0].id, "pass", "OK"))
        if len(cases) >= 2:
            seed_pairs.append((cases[1].id, "fail", "Bug: error message wrong"))
        if len(cases) >= 3:
            seed_pairs.append((cases[2].id, "blocked", "Email service down"))
        if len(cases) >= 4:
            seed_pairs.append((cases[3].id, "skipped", "Out of scope for smoke"))

        for tc_id, status, notes in seed_pairs:
            db.add(TestResult(test_run_id=run.id, test_case_id=tc_id, status=status, notes=notes))
        db.commit()

        project_id = project.id
        user_id = user.id
        run_id = run.id
        results_count = len(seed_pairs)


    print("Seed complete.")
    print(f"Project: {project_id} | User: {user_id} | New run: {run_id} | Results: {results_count}")



if __name__ == "__main__":
    main()
