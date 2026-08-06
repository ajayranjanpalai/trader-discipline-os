from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.export import export_trades_csv
from services.reports import generate_comprehensive_report

reports_bp = Blueprint("reports_bp", __name__)


@reports_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_report_summary():
    user_id = int(get_jwt_identity())
    period = request.args.get("period", "monthly")
    report = generate_comprehensive_report(user_id, period=period)
    return jsonify(report), 200


@reports_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_csv():
    user_id = int(get_jwt_identity())
    csv_data = export_trades_csv(user_id)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=trading_journal_export.csv"}
    )
