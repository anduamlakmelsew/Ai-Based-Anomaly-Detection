"""
PDF Report Generator for Security Scans
Generates professional PDF reports from scan results
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import json


class PDFReportGenerator:
    """Generate PDF reports from scan data"""
    
    def __init__(self, output_path):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#334155'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskCritical',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#dc2626'),
            fontSize=12,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#ea580c'),
            fontSize=12,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#ca8a04'),
            fontSize=12,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#16a34a'),
            fontSize=12,
            spaceAfter=6
        ))
    
    def generate_report(self, scan_data, report_title="Security Assessment Report"):
        """
        Generate a PDF report from scan data
        
        Args:
            scan_data: Dict containing scan results
            report_title: Title of the report
        """
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Title Page
        elements.append(Paragraph(report_title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        target = scan_data.get('target', 'Unknown')
        scan_type = scan_data.get('scan_type', 'Unknown')
        timestamp = scan_data.get('timestamp', datetime.now().isoformat())
        
        elements.append(Paragraph(f"<b>Target:</b> {target}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Scan Type:</b> {scan_type.upper()}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Generated:</b> {timestamp}", self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['CustomHeading2']))
        
        risk = scan_data.get('risk', {})
        risk_score = risk.get('score', 0)
        risk_level = risk.get('level', 'UNKNOWN')
        
        elements.append(Paragraph(
            f"This security assessment identified a <b>{risk_level}</b> risk level "
            f"with a risk score of <b>{risk_score}/100</b>.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Risk Summary Table
        elements.append(Paragraph("Risk Summary", self.styles['CustomHeading3']))
        
        findings = scan_data.get('findings', [])
        severity_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        
        for finding in findings:
            sev = finding.get('severity', 'LOW').upper()
            severity_count[sev] = severity_count.get(sev, 0) + 1
        
        risk_data = [
            ['Severity', 'Count'],
            ['CRITICAL', str(severity_count['CRITICAL'])],
            ['HIGH', str(severity_count['HIGH'])],
            ['MEDIUM', str(severity_count['MEDIUM'])],
            ['LOW', str(severity_count['LOW'])],
            ['Total', str(len(findings))]
        ]
        
        risk_table = Table(risk_data, colWidths=[3*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1f5f9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 1), (0, 1), colors.HexColor('#dc2626')),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 2), (0, 2), colors.HexColor('#ea580c')),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detailed Findings
        if findings:
            elements.append(PageBreak())
            elements.append(Paragraph("Detailed Findings", self.styles['CustomHeading2']))
            elements.append(Spacer(1, 0.2*inch))
            
            for idx, finding in enumerate(findings, 1):
                self._add_finding_to_elements(elements, finding, idx)
        
        # AI Analysis (if available)
        ai_analysis = scan_data.get('ai_analysis', {})
        if ai_analysis:
            elements.append(PageBreak())
            elements.append(Paragraph("AI Analysis", self.styles['CustomHeading2']))
            
            prediction = ai_analysis.get('prediction', 'unknown')
            confidence = ai_analysis.get('confidence', 0)
            
            elements.append(Paragraph(
                f"<b>Prediction:</b> {prediction.upper()}",
                self.styles['Normal']
            ))
            elements.append(Paragraph(
                f"<b>Confidence:</b> {confidence:.1%}",
                self.styles['Normal']
            ))
            
            if ai_analysis.get('features_used'):
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph("Features Analyzed:", self.styles['CustomHeading3']))
                
                features = ai_analysis['features_used']
                for key, value in features.items():
                    elements.append(Paragraph(f"• {key}: {value}", self.styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        return self.output_path
    
    def _add_finding_to_elements(self, elements, finding, index):
        """Add a single finding to the elements list"""
        severity = finding.get('severity', 'LOW').upper()
        finding_type = finding.get('type', 'Unknown')
        url = finding.get('url', 'N/A')
        evidence = finding.get('evidence', 'No evidence provided')
        
        # Choose style based on severity
        if severity == 'CRITICAL':
            style = self.styles['RiskCritical']
            color = '#dc2626'
        elif severity == 'HIGH':
            style = self.styles['RiskHigh']
            color = '#ea580c'
        elif severity == 'MEDIUM':
            style = self.styles['RiskMedium']
            color = '#ca8a04'
        else:
            style = self.styles['RiskLow']
            color = '#16a34a'
        
        # Finding header
        elements.append(Paragraph(
            f"Finding #{index}: {finding_type}",
            self.styles['CustomHeading3']
        ))
        
        # Severity badge
        elements.append(Paragraph(
            f"<b>Severity:</b> <font color='{color}'>{severity}</font>",
            style
        ))
        
        elements.append(Paragraph(f"<b>URL/Location:</b> {url}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Evidence:</b> {evidence}", self.styles['Normal']))
        
        if finding.get('exploits_available'):
            elements.append(Paragraph(
                f"<b>Exploits Available:</b> {len(finding['exploits_available'])}",
                self.styles['RiskHigh']
            ))
        
        elements.append(Spacer(1, 0.2*inch))


def generate_scan_report(scan_data, output_dir='reports'):
    """
    Convenience function to generate a report for a single scan
    
    Args:
        scan_data: Dictionary containing scan results
        output_dir: Directory to save the report
        
    Returns:
        Path to generated PDF file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    target = scan_data.get('target', 'unknown').replace('/', '_')
    filename = f"security_report_{target}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    generator = PDFReportGenerator(output_path)
    return generator.generate_report(scan_data)


def generate_consolidated_report(scans_data, output_dir='reports', title="Consolidated Security Report"):
    """
    Generate a consolidated report from multiple scans
    
    Args:
        scans_data: List of scan result dictionaries
        output_dir: Directory to save the report
        title: Report title
        
    Returns:
        Path to generated PDF file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"consolidated_report_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Aggregate findings
    all_findings = []
    for scan in scans_data:
        findings = scan.get('findings', [])
        for finding in findings:
            finding['source_scan'] = scan.get('target', 'Unknown')
            all_findings.append(finding)
    
    # Aggregate risk
    max_risk_score = max([s.get('risk', {}).get('score', 0) for s in scans_data] or [0])
    
    consolidated = {
        'target': 'Multiple Targets',
        'scan_type': 'consolidated',
        'timestamp': datetime.now().isoformat(),
        'findings': all_findings,
        'risk': {
            'score': max_risk_score,
            'level': 'HIGH' if max_risk_score > 50 else 'MEDIUM' if max_risk_score > 30 else 'LOW'
        },
        'scans_included': len(scans_data)
    }
    
    generator = PDFReportGenerator(output_path)
    return generator.generate_report(consolidated, title)
