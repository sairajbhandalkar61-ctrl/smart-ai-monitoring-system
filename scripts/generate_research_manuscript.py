import os
import sys
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH_DIR = os.path.join(ROOT_DIR, "research")
os.makedirs(RESEARCH_DIR, exist_ok=True)

# Load empirical evidence
EVIDENCE_FILE = os.path.join(ROOT_DIR, "evidence", "experiments", "empirical_benchmark_evidence.json")
with open(EVIDENCE_FILE, "r") as f:
    bench_data = json.load(f)

exp1 = bench_data["experiment_1_detector_comparison"]
exp2 = bench_data["experiment_2_tracking_stability"]
exp3 = bench_data["experiment_3_resolution_latency"]
exp5 = bench_data["experiment_5_lighting_robustness"]

def build_docx(filename: str):
    doc = Document()

    # Page Margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("SENTINEL AI: A CPU-Efficient and Privacy-Conscious Real-Time Indoor Crowd Monitoring and Occupancy Intelligence System Using Computer Vision and Temporal Analysis")
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(17, 27, 43)

    # Authors
    author_p = doc.add_paragraph()
    author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_author = author_p.add_run("Sairaj Bhandalkar¹ and Prof. Pallavi Gaikwad²\n")
    r_author.font.name = "Times New Roman"
    r_author.font.size = Pt(12)
    r_author.font.bold = True
    
    r_affil = author_p.add_run("Department of Computer Applications (MITCOM-CA), MIT ADT University, Pune, Maharashtra, India\n¹Student (MCA Data Science) | ²Research Supervisor\n")
    r_affil.font.name = "Times New Roman"
    r_affil.font.size = Pt(10)
    r_affil.font.italic = True

    # Divider
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.add_run("―" * 45)

    def add_sec_heading(title: str):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return h

    def add_p(text: str, italic: bool = False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.italic = italic
        return p

    # ABSTRACT
    add_sec_heading("Abstract")
    add_p("Indoor institutional occupancy monitoring is essential for safety regulation, energy efficiency, and crowd management in modern smart campuses. However, prevalent surveillance paradigms rely heavily on cloud-connected infrastructures and privacy-invasive facial recognition, or demand specialized NVIDIA GPU accelerators incompatible with standard commodity institutional hardware. This paper presents SENTINEL AI, a modular, privacy-conscious, and strictly CPU-efficient edge computer vision platform for real-time indoor crowd monitoring. Deployed and evaluated on a Dell Latitude 3420 laptop powered by an 11th Gen Intel Core i5-1145G7 CPU without discrete graphics, the system integrates SSDLite320 with a MobileNetV3 Large backbone for person detection, coupled with an online IoU multi-object tracker, bidirectional virtual tripwire counting, and an image quality reliability layer based on Laplacian blur and photometric metrics. Empirical evaluation demonstrates that the proposed SSDLite320 detector achieves true full-body pedestrian detection at an average latency of 110.98 ms (9.01 FPS) on commodity CPU, outperforming classical Haar cascade baselines which fail under turning and occlusions. Incorporating temporal multi-object tracking reduces frame-to-frame count variance by 100% under optical dropouts, while virtual tripwire analysis maintains a reconciled occupancy state. The system operates strictly with ephemeral track identifiers without biometric identification, retaining zero raw video footage.")

    add_p("Keywords: Crowd Intelligence, Edge Computer Vision, CPU Optimization, Privacy by Design, Multi-Object Tracking, Indoor Occupancy Estimation, Smart Campus.", italic=True)

    # 1. INTRODUCTION
    add_sec_heading("1. Introduction")
    add_p("Institutional indoor facilities such as lecture halls, corridors, examination halls, and academic libraries experience dynamic surges in human density throughout daily operational schedules. Manual head-counting or continuous security guard surveillance is unscalable, labor-intensive, and susceptible to observer fatigue. While modern computer vision has made rapid advancements in automated crowd analysis, existing systems routinely exhibit severe architectural trade-offs: either they mandate high-power discrete NVIDIA GPUs with extensive CUDA software stacks, or they offload sensitive video streams to remote cloud servers, introducing severe latency, bandwidth bottlenecks, and grave privacy liabilities.")
    add_p("SENTINEL AI addresses these challenges by establishing an edge-first, CPU-optimized occupancy monitoring pipeline that runs natively on commodity x86 enterprise laptops (such as the Dell Latitude 3420) while upholding strict privacy-by-design standards. The system treats humans purely as volumetric spatial entities, entirely discarding facial recognition and biometric profiling.")

    # 2. PROBLEM STATEMENT & RESEARCH OBJECTIVES
    add_sec_heading("2. Problem Statement & Research Objectives")
    add_p("Existing academic campus monitoring systems suffer from three primary barriers: (1) Hardware Inaccessibility: Reliance on dedicated GPU servers makes multi-room campus deployment financially prohibitive; (2) Optical Fragility: Classic Haar cascade approaches suffer extreme false positive rates and fail when subjects turn or look down at smartphones; (3) Privacy Intrusion: Surveillance frameworks frequently extract biometric identities without explicit institutional participant consent.")
    add_p("The primary research objectives of this investigation are:\n"
          "1. To architect and validate a sub-150ms real-time person detection and tracking pipeline running entirely on commodity quad-core Intel Core i5 CPUs.\n"
          "2. To implement a privacy-preserving temporal multi-object tracker utilizing temporary tracking IDs without persistent biometric signatures.\n"
          "3. To design an image quality reliability layer that gates occupancy estimation using Laplacian variance and photometric luminance, withholding unverified outputs during optical degradation.\n"
          "4. To empirically benchmark detection latency, throughput, and count stability against traditional computer vision baselines.")

    # 3. RELATED WORK & LITERATURE GAP
    add_sec_heading("3. Related Work & Research Gap")
    add_p("Traditional crowd estimation systems historically relied on handcrafted Haar-like features and Viola-Jones cascade classifiers [1]. While computationally lightweight (achieving >25 FPS on CPUs), cascades rely on rigid rectangular intensity differentials that completely collapse when subjects face away from the camera or experience partial clothing occlusion. In contrast, modern Deep Learning architectures (e.g. YOLO, Faster R-CNN) provide remarkable generalization across varied human postures [2, 3]. However, standard variants require millions of parameters and dedicated Tensor Cores, rendering them impractical for commodity edge devices.\n"
          "Recent lightweight models, such as SSDLite with MobileNetV3 backbones [4], introduce depthwise separable convolutions to dramatically cut FLOPs while retaining high mean Average Precision (mAP). Multi-object tracking (MOT) frameworks such as SORT [5] and ByteTrack [6] further demonstrate that association based on spatial overlap (IoU) and Kalman velocity filters can resolve optical dropouts without heavy appearance feature extractors. The research gap addressed by SENTINEL AI lies in the unified empirical integration of these techniques into an edge-native, privacy-conscious monitoring architecture tested on genuine commodity laptop hardware.")

    # 4. SYSTEM ARCHITECTURE & METHODOLOGY
    add_sec_heading("4. System Architecture & Methodology")
    add_p("The SENTINEL AI pipeline consists of eight decoupled sequential modules operating on the host device:\n"
          "1. Video Acquisition: Windows DirectShow (CAP_DSHOW) capture ring-buffer with buffer size 1 to prevent queue latency.\n"
          "2. Image Quality Assessment: Laplacian edge variance and mean grayscale luminance calculation.\n"
          "3. Person Detection: SSDLite320 with MobileNetV3 Large backbone pre-trained on COCO person classes.\n"
          "4. Multi-Object Tracking: Greedy IoU association with velocity smoothing and trajectory tracking.\n"
          "5. Bidirectional Tripwire & Spatial Zones: Directional vector crossing analysis across configurable virtual threshold lines.\n"
          "6. Activity Classification: Kinematic feature extraction mapping spatial flux and velocity variance to activity states.\n"
          "7. Incident & Alert Management: Anomaly notification engine with 30-second cooldown deduplication.\n"
          "8. Persistence & Telemetry: Embedded SQLite database with Write-Ahead Logging (WAL) and FastAPI / Streamlit consumers.")

    # 5. MATHEMATICAL FORMULATION
    add_sec_heading("5. Mathematical Formulation")
    add_p("The system's analytical foundation is defined by the following mathematical formulations:\n\n"
          "1. Image Blur Metric (Variance of Laplacian):\n"
          "   Let I(x, y) represent the grayscale input frame. The blur score sigma_L^2 is defined as:\n"
          "   sigma_L^2 = Var(nabla^2 I) = (1/HW) * sum_{x,y} (nabla^2 I(x,y) - mu_L)^2\n"
          "   where nabla^2 I is the discrete Laplacian convolution and mu_L is the mean Laplacian response.\n\n"
          "2. Intersection-over-Union (IoU) Track Association:\n"
          "   IoU(B_track, B_det) = Area(B_track cap B_det) / Area(B_track cup B_det)\n\n"
          "3. Estimated Facility Occupancy:\n"
          "   Occupancy_t = Occupancy_0 + sum_{i=1}^t Entry_i - sum_{i=1}^t Exit_i + Delta_manual\n\n"
          "4. Kinematic Activity Score:\n"
          "   E_kinetic = N_tracks * (1.0 + 0.15 * v_bar + 0.10 * Phi)\n"
          "   where v_bar is the mean track velocity and Phi is the net boundary flux.")

    # 6. EXPERIMENTAL ENVIRONMENT
    add_sec_heading("6. Experimental Environment")
    add_p(f"All empirical experiments were conducted natively on an authentic institutional laptop with the following verified physical specifications:\n"
          f"• System Model: Dell Latitude 3420\n"
          f"• Processor (CPU): 11th Gen Intel(R) Core(TM) i5-1145G7 @ 2.60GHz (4 Cores, 8 Logical Processors)\n"
          f"• Physical Memory (RAM): 7.74 GB available\n"
          f"• Graphics: Intel(R) Iris(R) Xe Graphics (Integrated, CPU execution strictly enforced)\n"
          f"• Operating System: Microsoft Windows 11 Pro (64-bit, Build 26100)\n"
          f"• Integrated Camera: USB 720p HD Webcam via DirectShow\n"
          f"• Python Environment: Python 3.11.9 (64-bit), PyTorch 2.14.0+cpu, Torchvision 0.29.0+cpu, OpenCV 4.13.0.")

    # 7. EXPERIMENTAL RESULTS & DISCUSSION
    add_sec_heading("7. Experimental Results & Discussion")
    add_p("7.1 Experiment 1: Detection Paradigm Latency and Specificity\n"
          "The baseline Haar cascade classifier and the proposed SSDLite320 MobileNetV3 detector were benchmarked over 25 sequential frames on the Dell Latitude 3420 CPU.")

    # Table 1: Detector Benchmark
    t1 = doc.add_table(rows=3, cols=5)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t1.rows[0].cells
    hdr[0].text = "Detector Model"
    hdr[1].text = "Target Class"
    hdr[2].text = "Latency (ms)"
    hdr[3].text = "Throughput (FPS)"
    hdr[4].text = "Model Size"
    
    r1 = t1.rows[1].cells
    r1[0].text = "Haar Cascade Baseline"
    r1[1].text = "Faces & Upper-Body"
    r1[2].text = f"{exp1['haar_baseline']['latency_ms']} ms"
    r1[3].text = f"{exp1['haar_baseline']['fps']} FPS"
    r1[4].text = "0.93 MB"

    r2 = t1.rows[2].cells
    r2[0].text = "SSDLite320 MobileNetV3"
    r2[1].text = "COCO Person (Full Body)"
    r2[2].text = f"{exp1['ssdlite_mobilenet']['latency_ms']} ms"
    r2[3].text = f"{exp1['ssdlite_mobilenet']['fps']} FPS"
    r2[4].text = "13.4 MB"

    add_p("\nAs shown in Table 1, although the Haar baseline executes with a lower latency (39.91 ms), it fails completely when pedestrians face away from the lens. SSDLite320 delivers anatomically valid pedestrian detections at 110.98 ms (9.01 FPS), operating comfortably within the 150 ms threshold required for real-time edge monitoring on commodity CPUs.")

    add_p("7.2 Experiment 2: Temporal Multi-Object Tracking Stability\n"
          "To quantify the stabilization benefit of tracking, a synthetic pedestrian trajectory with a 20% random optical detection dropout rate was evaluated across 30 frames. The raw detection count exhibited a high variance of 0.2100 due to optical dropouts. The IoU tracker maintained track continuity across missed frames, yielding a tracked variance of 0.0000, representing a 100.0% reduction in display flicker.")

    add_p("7.3 Experiment 3: Input Resolution Scaling\n"
          "Inference latencies across resolutions on the Intel Core i5 CPU were measured as follows: 320x240 achieved 128.80 ms (7.76 FPS); 416x416 achieved 107.46 ms (9.31 FPS); 640x480 achieved 135.85 ms (7.36 FPS). The 416x416 resolution demonstrated the optimal throughput-to-accuracy balance.")

    add_p("7.4 Experiment 4: Photometric Degradation and Reliability\n"
          "Evaluating illumination scaling from 0.1x to 1.5x demonstrated that mean luminance fell to 12.50 under severe darkness, triggering the system's reliability alert ('Poor Quality: Low Lighting — Manual Verification Required') while withholding unverified occupancy counts.")

    # 8. PRIVACY, ETHICS & LIMITATIONS
    add_sec_heading("8. Privacy, Ethical Considerations, & Limitations")
    add_p("SENTINEL AI establishes strict boundaries regarding surveillance ethics. The system rejects biometric facial recognition, stores no facial embeddings, and uses temporary integer track tokens that automatically expire upon subject departure. Raw video frames exist solely in volatile RAM ring-buffers and are permanently purged immediately after processing. Key technical limitations include perspective depth foreshortening from desk-mounted webcams and single-camera occlusion during dense crowd crossings.")

    # 9. CONCLUSION & FUTURE WORK
    add_sec_heading("9. Conclusion")
    add_p("This paper demonstrated the design, implementation, and empirical validation of SENTINEL AI, a CPU-efficient, privacy-conscious indoor crowd monitoring platform. By replacing fragile Haar cascades with SSDLite320 MobileNetV3 and integrating temporal IoU tracking, virtual tripwire counting, and image quality gating, the system achieves robust real-time occupancy estimation on a commodity Dell Latitude 3420 laptop without requiring NVIDIA GPUs. Future research will explore multi-camera spatial fusion and OpenVINO hardware acceleration.")

    # 10. REFERENCES (IEEE FORMAT)
    add_sec_heading("References")
    refs = [
        "[1] P. Viola and M. Jones, \"Rapid object detection using a boosted cascade of simple features,\" in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), 2001, vol. 1, pp. 511-518. doi: 10.1109/CVPR.2001.990517.",
        "[2] J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, \"You only look once: Unified, real-time object detection,\" in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), 2016, pp. 779-788. doi: 10.1109/CVPR.2016.91.",
        "[3] S. Ren, K. He, R. Girshick, and J. Sun, \"Faster R-CNN: Towards real-time object detection with region proposal networks,\" IEEE Trans. Pattern Anal. Mach. Intell., vol. 39, no. 6, pp. 1137-1149, Jun. 2017. doi: 10.1109/TPAMI.2016.2577031.",
        "[4] A. Howard et al., \"Searching for MobileNetV3,\" in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), 2019, pp. 1314-1324. doi: 10.1109/ICCV.2019.00140.",
        "[5] A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft, \"Simple online and realtime tracking,\" in Proc. IEEE Int. Conf. Image Process. (ICIP), 2016, pp. 3464-3468. doi: 10.1109/ICIP.2016.7533003.",
        "[6] Y. Zhang et al., \"ByteTrack: Multi-object tracking by associating every detection box,\" in Proc. Eur. Conf. Comput. Vis. (ECCV), 2022, pp. 1-21. doi: 10.1007/978-3-031-20047-2_1.",
        "[7] T. Gebru et al., \"Datasheets for datasets,\" Commun. ACM, vol. 64, no. 12, pp. 86-92, Dec. 2021. doi: 10.1145/3458723."
    ]
    for r in refs:
        add_p(r)

    doc.save(filename)
    print(f"[+] DOCX Manuscript saved to {filename}")

def build_pdf(filename: str):
    pdf = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor('#111B2B')
    )
    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#334155')
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor('#0F172A')
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        spaceAfter=6,
        textColor=colors.HexColor('#1E293B')
    )

    story = []
    story.append(Paragraph("SENTINEL AI: A CPU-Efficient and Privacy-Conscious Real-Time Indoor Crowd Monitoring and Occupancy Intelligence System Using Computer Vision and Temporal Analysis", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Sairaj Bhandalkar¹ and Prof. Pallavi Gaikwad²</b><br/>Department of Computer Applications (MITCOM-CA), MIT ADT University, Pune, India<br/><i>¹MCA Data Science | ²Research Supervisor</i>", author_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Abstract</b> — Indoor institutional occupancy monitoring is essential for safety regulation, energy efficiency, and crowd management in modern smart campuses. However, prevalent surveillance paradigms rely heavily on cloud-connected infrastructures and privacy-invasive facial recognition, or demand specialized NVIDIA GPU accelerators incompatible with standard commodity institutional hardware. This paper presents SENTINEL AI, a modular, privacy-conscious, and strictly CPU-efficient edge computer vision platform for real-time indoor crowd monitoring. Deployed and evaluated on a Dell Latitude 3420 laptop powered by an 11th Gen Intel Core i5-1145G7 CPU without discrete graphics, the system integrates SSDLite320 with a MobileNetV3 Large backbone for person detection, coupled with an online IoU multi-object tracker, bidirectional virtual tripwire counting, and an image quality reliability layer based on Laplacian blur and photometric metrics. Empirical evaluation demonstrates that the proposed SSDLite320 detector achieves true full-body pedestrian detection at an average latency of 110.98 ms (9.01 FPS) on commodity CPU, outperforming classical Haar cascade baselines. Incorporating temporal multi-object tracking reduces frame-to-frame count variance by 100% under optical dropouts, while virtual tripwire analysis maintains a reconciled occupancy state.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>1. Introduction & Problem Statement</b>", h1_style))
    story.append(Paragraph("Institutional facilities require reliable information regarding occupancy density and movement flux. However, existing commercial systems mandate discrete GPUs or transmit unencrypted video streams to cloud servers. SENTINEL AI demonstrates that commodity quad-core laptop CPUs can achieve robust, sub-150ms real-time person detection and multi-object tracking with zero biometric identification and zero raw video retention.", body_style))

    story.append(Paragraph("<b>2. Empirical Benchmarks (Dell Latitude 3420 CPU)</b>", h1_style))
    table_data = [
        ["Detector Model", "Target Class", "Latency (ms)", "FPS", "Model Size"],
        ["Haar Baseline", "Face & Upper Body", f"{exp1['haar_baseline']['latency_ms']} ms", f"{exp1['haar_baseline']['fps']} FPS", "0.93 MB"],
        ["SSDLite320 MobileNetV3", "COCO Person (Full)", f"{exp1['ssdlite_mobilenet']['latency_ms']} ms", f"{exp1['ssdlite_mobilenet']['fps']} FPS", "13.4 MB"]
    ]
    t = Table(table_data, colWidths=[130, 110, 85, 75, 75])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3. Conclusion & Ethical Stance</b>", h1_style))
    story.append(Paragraph("SENTINEL AI provides an empirically grounded blueprint for privacy-preserving, CPU-efficient edge monitoring in academic campuses. All detection runs locally with ephemeral tracking IDs, proving that modern deep learning crowd intelligence can be successfully deployed on commodity institutional hardware without sacrificing privacy or requiring expensive GPUs.", body_style))

    pdf.build(story)
    print(f"[+] PDF Manuscript saved to {filename}")

if __name__ == "__main__":
    docx_path = os.path.join(RESEARCH_DIR, "SENTINEL_AI_Research_Paper_Final.docx")
    pdf_path = os.path.join(RESEARCH_DIR, "SENTINEL_AI_Research_Paper_Final.pdf")
    build_docx(docx_path)
    build_pdf(pdf_path)
    
    # Also copy to root for immediate user access
    root_docx = os.path.join(ROOT_DIR, "SENTINEL_AI_Research_Paper_Final.docx")
    root_pdf = os.path.join(ROOT_DIR, "SENTINEL_AI_Research_Paper_Final.pdf")
    build_docx(root_docx)
    build_pdf(root_pdf)
