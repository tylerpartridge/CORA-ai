#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/pdf_exporter.py
🎯 PURPOSE: Professional PDF export system for profit intelligence reports
🔗 IMPORTS: reportlab, datetime, json
📤 EXPORTS: ProfitIntelligencePDFExporter class
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import io

class ProfitIntelligencePDFExporter:
    """Professional PDF export system for profit intelligence reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for professional reports"""
        # Check if styles already exist before adding
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#8B00FF'),  # CORA purple
                alignment=TA_CENTER
            ))
        
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.HexColor('#2D3748'),
                alignment=TA_LEFT
            ))
        
        if 'Subsection' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Subsection',
                parent=self.styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                textColor=colors.HexColor('#4A5568'),
                alignment=TA_LEFT
            ))
        
        # Body text style - override existing
        if 'BodyText' in self.styles:
            self.styles['BodyText'].fontSize = 11
            self.styles['BodyText'].spaceAfter = 6
            self.styles['BodyText'].textColor = colors.HexColor('#2D3748')
            self.styles['BodyText'].alignment = TA_LEFT
        
        if 'Metric' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Metric',
                parent=self.styles['Normal'],
                fontSize=12,
                spaceAfter=4,
                textColor=colors.HexColor('#8B00FF'),
                alignment=TA_LEFT,
                fontName='Helvetica-Bold'
            ))
        
    def create_cover_page(self, story: List, data: Dict[str, Any]):
        """Create professional cover page"""
        # Company logo placeholder
        story.append(Paragraph("CORA AI", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Report title
        story.append(Paragraph("Profit Intelligence Report", self.styles['SectionHeader']))
        story.append(Spacer(1, 30))
        
        # Intelligence score
        score = data.get('intelligenceScore', 0)
        grade = data.get('letterGrade', 'N/A')
        story.append(Paragraph(f"Business Intelligence Score: {score}/100 ({grade})", self.styles['Metric']))
        story.append(Spacer(1, 20))
        
        # Report metadata
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['BodyText']))
        story.append(Paragraph(f"Report Period: Last 30 Days", self.styles['BodyText']))
        story.append(Spacer(1, 40))
        
        # Executive summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"This report provides comprehensive analysis of your business performance, "
            f"including cost forecasting, vendor performance, job profitability predictions, "
            f"pricing optimization, and industry benchmarks. Your intelligence score of {score}/100 "
            f"indicates {'excellent' if score >= 80 else 'good' if score >= 60 else 'needs improvement'} "
            f"business health.",
            self.styles['BodyText']
        ))
        
    def create_forecasting_section(self, story: List, data: Dict[str, Any]):
        """Create cost forecasting section with charts"""
        story.append(Paragraph("1. Cost Forecasting Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        # Forecast data
        forecast = data.get('forecast', {})
        months = forecast.get('months', [])
        actual = forecast.get('actual', [])
        predicted = forecast.get('predicted', [])
        
        # Summary metrics
        story.append(Paragraph("Forecast Summary", self.styles['Subsection']))
        
        if actual and predicted:
            current_avg = sum(actual) / len(actual)
            future_avg = sum([x for x in predicted if x is not None]) / len([x for x in predicted if x is not None])
            trend = ((future_avg - current_avg) / current_avg) * 100
            
            story.append(Paragraph(f"Current Average Monthly Costs: ${current_avg:,.0f}", self.styles['BodyText']))
            story.append(Paragraph(f"Predicted Average Monthly Costs: ${future_avg:,.0f}", self.styles['BodyText']))
            story.append(Paragraph(f"Cost Trend: {trend:+.1f}%", self.styles['Metric']))
            story.append(Spacer(1, 10))
        
        # Forecast table
        if months and actual:
            table_data = [['Month', 'Actual Costs', 'Predicted Costs', 'Variance']]
            for i, month in enumerate(months):
                actual_val = actual[i] if i < len(actual) else 'N/A'
                pred_val = predicted[i] if i < len(predicted) and predicted[i] is not None else 'N/A'
                variance = 'N/A'
                if isinstance(actual_val, (int, float)) and isinstance(pred_val, (int, float)):
                    variance = f"${pred_val - actual_val:+,.0f}"
                
                table_data.append([month, f"${actual_val:,.0f}" if isinstance(actual_val, (int, float)) else actual_val,
                                 f"${pred_val:,.0f}" if isinstance(pred_val, (int, float)) else pred_val, variance])
            
            forecast_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
            forecast_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B00FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(forecast_table)
            story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Forecasting Recommendations", self.styles['Subsection']))
        story.append(Paragraph(
            "• Monitor cost trends closely and adjust budgets accordingly<br/>"
            "• Consider seasonal variations in your planning<br/>"
            "• Review vendor contracts to optimize costs<br/>"
            "• Implement cost control measures for predicted increases",
            self.styles['BodyText']
        ))
        
    def create_vendor_section(self, story: List, data: Dict[str, Any]):
        """Create vendor performance analysis section"""
        story.append(Paragraph("2. Vendor Performance Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        vendors = data.get('vendors', [])
        
        if vendors:
            # Top performers
            story.append(Paragraph("Top Performing Vendors", self.styles['Subsection']))
            
            vendor_data = [['Vendor', 'Performance Score', 'Total Cost', 'Trend']]
            for vendor in vendors[:5]:  # Top 5 vendors
                vendor_data.append([
                    vendor.get('name', 'Unknown'),
                    f"{vendor.get('performance', 0)}%",
                    f"${vendor.get('cost', 0):,.0f}",
                    f"{vendor.get('trend', 0):+.1f}%"
                ])
            
            vendor_table = Table(vendor_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
            vendor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B00FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(vendor_table)
            story.append(Spacer(1, 20))
        
        # Vendor recommendations
        story.append(Paragraph("Vendor Optimization Recommendations", self.styles['Subsection']))
        story.append(Paragraph(
            "• Negotiate better terms with high-cost, low-performance vendors<br/>"
            "• Increase business with top-performing vendors<br/>"
            "• Consider consolidating purchases with fewer vendors for better pricing<br/>"
            "• Monitor vendor trends and address declining performance",
            self.styles['BodyText']
        ))
        
    def create_job_section(self, story: List, data: Dict[str, Any]):
        """Create job profitability predictions section"""
        story.append(Paragraph("3. Job Profitability Predictions", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        jobs = data.get('jobs', [])
        
        if jobs:
            # Job analysis
            story.append(Paragraph("Current Job Analysis", self.styles['Subsection']))
            
            job_data = [['Job', 'Risk Level', 'Potential Profit', 'Completion %']]
            for job in jobs:
                risk_color = {
                    'high': colors.red,
                    'medium': colors.orange,
                    'low': colors.green
                }.get(job.get('risk', 'medium'), colors.black)
                
                job_data.append([
                    job.get('name', 'Unknown'),
                    job.get('risk', 'Unknown').title(),
                    f"${job.get('potential', 0):,.0f}",
                    f"{job.get('completion', 0)}%"
                ])
            
            job_table = Table(job_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1*inch])
            job_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B00FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(job_table)
            story.append(Spacer(1, 20))
        
        # Job recommendations
        story.append(Paragraph("Job Management Recommendations", self.styles['Subsection']))
        story.append(Paragraph(
            "• Focus resources on high-profit, low-risk jobs<br/>"
            "• Implement additional monitoring for high-risk projects<br/>"
            "• Review pricing strategy for similar future jobs<br/>"
            "• Consider project management improvements for delayed jobs",
            self.styles['BodyText']
        ))
        
    def create_pricing_section(self, story: List, data: Dict[str, Any]):
        """Create pricing intelligence section"""
        story.append(Paragraph("4. Pricing Intelligence", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        pricing = data.get('pricing', {})
        
        # Market comparison
        story.append(Paragraph("Market Pricing Analysis", self.styles['Subsection']))
        story.append(Paragraph(f"Market Average: ${pricing.get('marketAverage', 0):.0f}/hr", self.styles['BodyText']))
        story.append(Paragraph(f"Your Average: ${pricing.get('yourAverage', 0):.0f}/hr", self.styles['BodyText']))
        
        price_diff = pricing.get('yourAverage', 0) - pricing.get('marketAverage', 0)
        if price_diff > 0:
            story.append(Paragraph(f"Pricing Premium: +${price_diff:.0f}/hr above market", self.styles['Metric']))
        else:
            story.append(Paragraph(f"Pricing Gap: ${price_diff:.0f}/hr below market", self.styles['Metric']))
        
        story.append(Spacer(1, 15))
        
        # Service-specific recommendations
        recommendations = pricing.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Service-Specific Pricing Recommendations", self.styles['Subsection']))
            
            rec_data = [['Service', 'Current Price', 'Suggested Price', 'Confidence']]
            for rec in recommendations:
                rec_data.append([
                    rec.get('service', 'Unknown'),
                    f"${rec.get('currentPrice', 0):.0f}/hr",
                    f"${rec.get('suggestedPrice', 0):.0f}/hr",
                    f"{rec.get('confidence', 0)}%"
                ])
            
            rec_table = Table(rec_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B00FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(rec_table)
            story.append(Spacer(1, 20))
        
        # Pricing recommendations
        story.append(Paragraph("Pricing Strategy Recommendations", self.styles['Subsection']))
        story.append(Paragraph(
            "• Consider gradual price increases for services below market average<br/>"
            "• Maintain premium pricing for high-value services<br/>"
            "• Monitor competitor pricing regularly<br/>"
            "• Adjust pricing based on demand and seasonality",
            self.styles['BodyText']
        ))
        
    def create_benchmarks_section(self, story: List, data: Dict[str, Any]):
        """Create industry benchmarks section"""
        story.append(Paragraph("5. Industry Benchmarks", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        benchmarks = data.get('benchmarks', {})
        
        # Benchmark comparison
        story.append(Paragraph("Performance vs Industry Standards", self.styles['Subsection']))
        
        metrics = [
            ('Profit Margin', 'profitMargin'),
            ('Completion Rate', 'completionRate'),
            ('Customer Satisfaction', 'satisfaction'),
            ('Operational Efficiency', 'efficiency')
        ]
        
        benchmark_data = [['Metric', 'Your Performance', 'Industry Average', 'Status']]
        for metric_name, metric_key in metrics:
            your_val = benchmarks.get(metric_key, {}).get('your', 0)
            industry_val = benchmarks.get(metric_key, {}).get('industry', 0)
            
            if your_val > industry_val:
                status = "Above Average"
                status_color = colors.green
            elif your_val < industry_val:
                status = "Below Average"
                status_color = colors.red
            else:
                status = "Average"
                status_color = colors.orange
            
            benchmark_data.append([
                metric_name,
                f"{your_val:.1f}%",
                f"{industry_val:.1f}%",
                status
            ])
        
        benchmark_table = Table(benchmark_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        benchmark_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B00FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(benchmark_table)
        story.append(Spacer(1, 20))
        
        # Benchmark recommendations
        story.append(Paragraph("Benchmark Improvement Recommendations", self.styles['Subsection']))
        story.append(Paragraph(
            "• Focus on areas where you're below industry average<br/>"
            "• Leverage your strengths in above-average areas<br/>"
            "• Set specific improvement targets for each metric<br/>"
            "• Monitor progress monthly and adjust strategies accordingly",
            self.styles['BodyText']
        ))
        
    def create_action_plan(self, story: List, data: Dict[str, Any]):
        """Create actionable recommendations section"""
        story.append(Paragraph("Action Plan & Next Steps", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        # Priority actions
        story.append(Paragraph("Priority Actions (Next 30 Days)", self.styles['Subsection']))
        story.append(Paragraph(
            "1. <b>Immediate (Week 1):</b> Review vendor contracts and negotiate better terms<br/>"
            "2. <b>Short-term (Week 2-3):</b> Implement pricing adjustments for below-market services<br/>"
            "3. <b>Medium-term (Week 4):</b> Develop cost control measures for predicted increases<br/>"
            "4. <b>Ongoing:</b> Monitor job profitability and adjust resource allocation",
            self.styles['BodyText']
        ))
        
        story.append(Spacer(1, 15))
        
        # Expected outcomes
        story.append(Paragraph("Expected Outcomes", self.styles['Subsection']))
        story.append(Paragraph(
            "• 10-15% improvement in profit margins<br/>"
            "• 5-10% reduction in operational costs<br/>"
            "• Better vendor relationships and pricing<br/>"
            "• Improved job profitability tracking<br/>"
            "• Enhanced competitive positioning",
            self.styles['BodyText']
        ))
        
    def generate_profit_intelligence_report(self, data: Dict[str, Any], output_path: str = None) -> str:
        """Generate comprehensive profit intelligence PDF report"""
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/profit_intelligence_report_{timestamp}.pdf"
        
        # Ensure reports directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        story = []
        
        # Build report sections
        self.create_cover_page(story, data)
        story.append(Spacer(1, 20))
        
        self.create_forecasting_section(story, data)
        story.append(Spacer(1, 20))
        
        self.create_vendor_section(story, data)
        story.append(Spacer(1, 20))
        
        self.create_job_section(story, data)
        story.append(Spacer(1, 20))
        
        self.create_pricing_section(story, data)
        story.append(Spacer(1, 20))
        
        self.create_benchmarks_section(story, data)
        story.append(Spacer(1, 20))
        
        self.create_action_plan(story, data)
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def generate_section_report(self, section: str, data: Dict[str, Any], output_path: str = None) -> str:
        """Generate PDF report for a specific section"""
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/{section}_report_{timestamp}.pdf"
        
        # Ensure reports directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        story = []
        
        # Section-specific content
        if section == "forecasting":
            self.create_cover_page(story, data)
            story.append(Spacer(1, 20))
            self.create_forecasting_section(story, data)
        elif section == "vendors":
            self.create_cover_page(story, data)
            story.append(Spacer(1, 20))
            self.create_vendor_section(story, data)
        elif section == "jobs":
            self.create_cover_page(story, data)
            story.append(Spacer(1, 20))
            self.create_job_section(story, data)
        elif section == "pricing":
            self.create_cover_page(story, data)
            story.append(Spacer(1, 20))
            self.create_pricing_section(story, data)
        elif section == "benchmarks":
            self.create_cover_page(story, data)
            story.append(Spacer(1, 20))
            self.create_benchmarks_section(story, data)
        
        # Build PDF
        doc.build(story)
        
        return output_path

# Global exporter instance
pdf_exporter = ProfitIntelligencePDFExporter() 

# Backwards-compat
PDFExporter = ProfitIntelligencePDFExporter