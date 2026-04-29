from app import db
from datetime import datetime


class Scan(db.Model):
    __tablename__ = "scans"

    # =========================
    # 🆔 IDENTIFIERS
    # =========================
    id = db.Column(db.Integer, primary_key=True)

    target = db.Column(db.String(255), nullable=False, index=True)
    scan_type = db.Column(db.String(50), nullable=False, index=True)

    # =========================
    # 🔥 CORE SCAN DATA
    # =========================
    # NOTE: avoid mutable defaults ([] / {}) directly → use default callable
    open_ports = db.Column(db.JSON, default=list, nullable=False)
    services = db.Column(db.JSON, default=list, nullable=False)
    os_info = db.Column(db.JSON, default=dict, nullable=False)
    vulnerabilities = db.Column(db.JSON, default=list, nullable=False)
    findings = db.Column(db.JSON, default=list, nullable=False)

    # =========================
    # 🧠 RISK
    # =========================
    risk_score = db.Column(db.Float, default=0.0, nullable=False)

    # =========================
    # 🚀 EXECUTION STATE
    # =========================
    status = db.Column(
        db.String(50),
        default="queued",
        nullable=False,
        index=True
    )  # queued, running, completed, failed

    progress = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )  # 0 → 100

    # Celery async task tracking
    celery_task_id = db.Column(
        db.String(255),
        nullable=True,
        index=True
    )

    # =========================
    # 📦 FULL RESULT (SOURCE OF TRUTH)
    # =========================
    result = db.Column(db.JSON, nullable=True)

    # =========================
    # 👤 OWNERSHIP
    # =========================
    user_id = db.Column(db.Integer, nullable=False, index=True)

    # =========================
    # ⏱ TIMESTAMPS
    # =========================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =========================
    # 🔧 HELPER METHODS
    # =========================
    def set_result(self, result_dict: dict):
        """
        Safely set scan result + sync important fields
        """
        self.result = result_dict or {}

        data = self.result.get("data", {})

        # sync important fields for fast queries
        self.findings = data.get("findings", [])
        self.vulnerabilities = data.get("findings", [])

        self.risk_score = (
            data.get("risk_analysis", {}).get("total_risk_score", 0)
        )

        self.progress = 100
        self.status = "completed"

    def mark_failed(self, message: str = ""):
        self.status = "failed"
        self.progress = 100

        self.result = {
            "success": False,
            "message": message
        }

    def to_dict(self):
        """
        Standardized output for API / dashboard
        """
        data = (self.result or {}).get("data", {})

        return {
            "id": self.id,
            "target": self.target,
            "scan_type": self.scan_type,
            "status": self.status,
            "progress": self.progress,
            "celery_task_id": self.celery_task_id,
            "date": self.created_at.isoformat(),

            # 🔥 dashboard-critical fields
            "findings": data.get("findings", []),
            "risk": {
                "score": data.get("risk_analysis", {}).get("total_risk_score", 0),
                "level": data.get("risk_analysis", {}).get("risk_level", "LOW")
            },
            "total_urls_scanned": data.get("total_urls_scanned", 0)
        }

    def to_task_status_dict(self):
        """
        Return scan status suitable for Celery task status endpoint
        """
        return {
            "scan_id": self.id,
            "celery_task_id": self.celery_task_id,
            "target": self.target,
            "scan_type": self.scan_type,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "result": self.result if self.status in ["completed", "failed"] else None
        }