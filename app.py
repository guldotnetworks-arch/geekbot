import os
import json
from datetime import date, datetime, timedelta
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///productivity.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    total_seconds = db.Column(db.Integer, default=0)


class PomodoroSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration_seconds = db.Column(db.Integer, default=0)
    session_type = db.Column(db.String(10), default="work")  # work | break


with app.app_context():
    db.create_all()


# ── Task API ──────────────────────────────────────────────────────────────────

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    day = request.args.get("date", str(date.today()))
    start = datetime.strptime(day, "%Y-%m-%d")
    end = start + timedelta(days=1)
    tasks = Task.query.filter(Task.created_at >= start, Task.created_at < end).all()
    return jsonify([_task_dict(t) for t in tasks])


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    task = Task(title=data["title"])
    db.session.add(task)
    db.session.commit()
    return jsonify(_task_dict(task)), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if "done" in data:
        task.done = data["done"]
        task.completed_at = datetime.utcnow() if data["done"] else None
    if "total_seconds" in data:
        task.total_seconds = data["total_seconds"]
    if "title" in data:
        task.title = data["title"]
    db.session.commit()
    return jsonify(_task_dict(task))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return "", 204


# ── Session API ───────────────────────────────────────────────────────────────

@app.route("/api/sessions", methods=["POST"])
def log_session():
    data = request.get_json()
    session = PomodoroSession(
        task_id=data.get("task_id"),
        duration_seconds=data.get("duration_seconds", 0),
        session_type=data.get("session_type", "work"),
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({"id": session.id}), 201


# ── Stats API ─────────────────────────────────────────────────────────────────

@app.route("/api/stats")
def get_stats():
    day = request.args.get("date", str(date.today()))
    start = datetime.strptime(day, "%Y-%m-%d")
    end = start + timedelta(days=1)

    tasks_today = Task.query.filter(Task.created_at >= start, Task.created_at < end).all()
    sessions_today = PomodoroSession.query.filter(
        PomodoroSession.started_at >= start,
        PomodoroSession.started_at < end,
        PomodoroSession.session_type == "work",
    ).all()

    total_focus = sum(s.duration_seconds for s in sessions_today)
    completed = sum(1 for t in tasks_today if t.done)

    # Last 7 days history for the chart
    history = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        d_start = datetime(d.year, d.month, d.day)
        d_end = d_start + timedelta(days=1)
        s = PomodoroSession.query.filter(
            PomodoroSession.started_at >= d_start,
            PomodoroSession.started_at < d_end,
            PomodoroSession.session_type == "work",
        ).all()
        history.append({
            "date": str(d),
            "focus_minutes": sum(x.duration_seconds for x in s) // 60,
        })

    return jsonify({
        "tasks_total": len(tasks_today),
        "tasks_done": completed,
        "pomodoros": len(sessions_today),
        "focus_minutes": total_focus // 60,
        "history": history,
    })


# ── Main ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


def _task_dict(t):
    return {
        "id": t.id,
        "title": t.title,
        "done": t.done,
        "created_at": t.created_at.isoformat(),
        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        "total_seconds": t.total_seconds,
    }


if __name__ == "__main__":
    app.run(debug=True)
