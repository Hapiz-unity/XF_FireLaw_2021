"""
PDF report generator using reportlab
Generates simple PDF reports and saves to 04_output/demo_report_samples/
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import os
from pathlib import Path

def generate_pdf_report(work_order, location, iot_snapshot, output_dir: str = None):
    """
    Generate PDF report for a work order
    
    Args:
        work_order: WorkOrder model instance
        location: Location model instance
        iot_snapshot: IoTSnapshot model instance
        output_dir: Directory to save PDF (defaults to env REPORT_OUTPUT_DIR or 04_output/demo_report_samples/)
    
    Returns:
        Path to generated PDF file
    """
    # Determine output directory
    if output_dir is None:
        output_dir = os.getenv("REPORT_OUTPUT_DIR", "./04_output/demo_report_samples")
    
    # Create directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{work_order.id}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "消防水泵维保履职尽责报告")
    
    # Work Order Info
    y = height - 3.5*cm
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, y, f"工单编号: {work_order.id}")
    y -= 0.6*cm
    c.drawString(2*cm, y, f"点位: {location.name}")
    y -= 0.6*cm
    c.drawString(2*cm, y, f"打卡时间: {work_order.checkin_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Work Order Fields
    y -= 1*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "维保检查项:")
    y -= 0.6*cm
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, y, f"泵房: {work_order.pumphouse}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"末端: {work_order.endpoint}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"栓: {work_order.hydrant}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"联动: {work_order.linkage}")
    y -= 0.5*cm
    if work_order.conclusion:
        c.drawString(2*cm, y, f"结论: {work_order.conclusion}")
        y -= 0.5*cm
    
    # IoT Snapshot
    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "IoT快照:")
    y -= 0.6*cm
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, y, f"压力: {iot_snapshot.pressure} MPa")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"泵运行状态: {iot_snapshot.pump_running}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"快照时间: {iot_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Legal Mapping Placeholder
    y -= 1*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "法规映射:")
    y -= 0.6*cm
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, y, "法规映射展示占位")
    
    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, 2*cm, f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    c.save()
    return filepath

