import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Professional Color Palette
    NAVY = RGBColor(15, 45, 95)       # #0F2D5F
    LIGHT_BG = RGBColor(248, 250, 252)# #F8FAFC
    CARD_BG = RGBColor(255, 255, 255) # White
    BORDER_COLOR = RGBColor(218, 225, 233)
    TEXT_DARK = RGBColor(33, 37, 41)
    TEXT_MUTED = RGBColor(100, 116, 139)
    ACCENT_BLUE = RGBColor(2, 136, 209)
    ACCENT_GREEN = RGBColor(46, 125, 50)

    def add_header(slide, title_text, category_text="ESA TERM PAPER | PROJECT 15"):
        # Header banner container
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.9))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Calibri"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Calibri"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    # =============================================================
    # SLIDE 1: Title Page
    # =============================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Inner decorative container
    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.8), Inches(11.333), Inches(5.9))
    card1.fill.solid()
    card1.fill.fore_color.rgb = RGBColor(23, 58, 115)
    card1.line.color.rgb = RGBColor(41, 88, 166)
    card1.line.width = Pt(1.5)

    tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "ENERGY SYSTEM ANALYTICS (EE 1331) | TERM PAPER PROJECT 15"
    p.font.name = "Calibri"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(144, 202, 249)
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "Machine Learning-Based Transmission Line Fault Type Classification for Intelligent Power System Protection"
    p.font.name = "Calibri"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.space_after = Pt(18)

    p = tf1.add_paragraph()
    p.text = "High-Accuracy Multiclass SVM Classification & Sub-Cycle Digital Relay Prototype Module"
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(207, 216, 220)
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "Student Team: Rishabh Raturi (24EEB0A55) | Simhadri Yateesh Sai (24EEB0A59)\n" \
             "Faculty Guide: Prof. Debasmita Panda\n" \
             "Department: Department of Electrical & Electronics Engineering, 5th Sem 2026–2027"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.font.bold = False

    # =============================================================
    # SLIDE 2: Problem Background & Objectives
    # =============================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Problem Context & Project Objectives")

    # Card Left: Background & Limitations
    c_left = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = CARD_BG
    c_left.line.color.rgb = BORDER_COLOR
    tb_l = s2.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(5.0))
    tfl = tb_l.text_frame
    tfl.word_wrap = True

    p = tfl.paragraphs[0]
    p.text = "1. Background & Limitations of Relaying"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)

    bullets_l = [
        "Transmission lines are vulnerable to weather, lightning, and insulation failure.",
        "Fault Types: Single Line-to-Ground (LG, 70-80%), Line-to-Line (LL, 15%), Double Line-to-Ground (LLG, 10%), and Three-Phase (LLL, 5%).",
        "Conventional Distance Relays: Rely on fixed impedance reach zones (mho / quadrilateral) on the R-X plane.",
        "Key Challenges: High fault resistance causes under-reach, power swings trigger false trips, and manual setting updates are required on topology changes."
    ]
    for b in bullets_l:
        p = tfl.add_paragraph()
        p.text = "• " + b
        p.font.name = "Calibri"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # Card Right: Objectives
    c_right = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = CARD_BG
    c_right.line.color.rgb = BORDER_COLOR
    tb_r = s2.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(5.0))
    tfr = tb_r.text_frame
    tfr.word_wrap = True

    p = tfr.paragraphs[0]
    p.text = "2. Project Goals & Proposed Approach"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)

    bullets_r = [
        "Dataset Ingestion: 110 kV transmission network simulated via DIgSILENT PowerFactory (IEC 60909 fault sweep & load flow).",
        "Intelligent Pattern Recognition: Use Support Vector Machines (SVMs) to classify disturbances directly from 24 voltage and current channels.",
        "Selective Tripping: Enable single-pole tripping for LG faults to preserve transient stability and 3-pole tripping for multiphase faults.",
        "Prototype Protection Module: Build a standalone Python module with verified sub-cycle latency (< 20 ms) for real-time digital relay deployment."
    ]
    for b in bullets_r:
        p = tfr.add_paragraph()
        p.text = "• " + b
        p.font.name = "Calibri"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # =============================================================
    # SLIDE 3: Flow Chart / System Architecture (Requirement 4)
    # =============================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "System Architecture & Algorithmic Workflow")

    # Insert block diagram figure
    diag_path = "plots/fig_block_diagram.png"
    if os.path.exists(diag_path):
        s3.shapes.add_picture(diag_path, Inches(0.8), Inches(1.4), Inches(11.733))

    # Explanation cards underneath
    steps_info = [
        ("1. Data Ingestion & Audit", "618 samples x 24 sensors (9 voltages in kV, 15 currents in kA). 0 nulls in measurements."),
        ("2. Deduplication & Prep", "Pruned 73 static load-flow duplicates. Kept high current spikes as physical fault signatures."),
        ("3. Scaling & Split", "StandardScaler (mean 0, var 1) fit on train only. Stratified 70/15/15 train/val/test split."),
        ("4. SVM Tuning & Relay Trip", "5-fold Stratified CV for kernel, C, and gamma. Sub-cycle inference triggers selective tripping.")
    ]
    card_w = Inches(2.78)
    card_gap = Inches(0.2)
    for i, (st, desc) in enumerate(steps_info):
        x = Inches(0.8) + i * (card_w + card_gap)
        c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(4.7), card_w, Inches(2.2))
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = BORDER_COLOR
        tb = s3.shapes.add_textbox(x + Inches(0.15), Inches(4.8), card_w - Inches(0.3), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = st
        p.font.name = "Calibri"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(4)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # =============================================================
    # SLIDE 4: Machine Learning Model & Training Strategy
    # =============================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Support Vector Machine Formulation & Tuning")

    # Card Left: Math Formulation
    c_m = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    c_m.fill.solid()
    c_m.fill.fore_color.rgb = CARD_BG
    c_m.line.color.rgb = BORDER_COLOR
    tbm = s4.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(5.0))
    tfm = tbm.text_frame
    tfm.word_wrap = True

    p = tfm.paragraphs[0]
    p.text = "1. SVM Soft-Margin Optimization"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    p = tfm.add_paragraph()
    p.text = "Primal Objective Function:\nmin (1/2 ||w||² + C Σ ξᵢ)\ns.t.  yᵢ (wᵀ φ(xᵢ) + b) ≥ 1 - ξᵢ,  ξᵢ ≥ 0"
    p.font.name = "Consolas"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(15, 76, 129)
    p.space_after = Pt(10)

    bullets_svm = [
        "Margin Maximization: Finds the unique hyperplane with the largest geometric margin between fault classes.",
        "Convex Formulation: Solved via quadratic programming; guaranteed global minimum without local optima.",
        "Kernels Evaluated: Linear K(x, x') = xᵀx' and Radial Basis Function (RBF) K(x, x') = exp(-γ ||x - x'||²).",
        "Multiclass Strategy: One-vs-One (OvO) with majority voting across 6 pairwise binary classifiers."
    ]
    for b in bullets_svm:
        p = tfm.add_paragraph()
        p.text = "• " + b
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # Card Right: Tuning & Results
    c_t = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4))
    c_t.fill.solid()
    c_t.fill.fore_color.rgb = CARD_BG
    c_t.line.color.rgb = BORDER_COLOR
    tbt = s4.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(5.0))
    tft = tbt.text_frame
    tft.word_wrap = True

    p = tft.paragraphs[0]
    p.text = "2. Stratified Data Split & Grid Search"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    bullets_tun = [
        "Partitioning: 70% Train (381), 15% Validation (82), 15% Test (82).",
        "Cross-Validation: 5-Fold Stratified K-Fold on training partition.",
        "Grid Parameters: Kernel ∈ {linear, rbf}, C ∈ {0.1, 1, 10, 100}, γ ∈ {scale, 0.01, 0.1, 1}.",
        "Optimal Settings:\n  - Linear Kernel: C = 0.1 (CV Macro F1 = 1.0000)\n  - RBF Kernel: C = 1.0, γ = 'scale' (CV Macro F1 = 1.0000)",
        "Both kernels achieve 100% cross-validation score due to strong physical separation in the 24-sensor space."
    ]
    for b in bullets_tun:
        p = tft.add_paragraph()
        p.text = "• " + b
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # =============================================================
    # SLIDE 5: Results & Performance Evaluation
    # =============================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Experimental Results & Model Evaluation")

    # Images: Confusion matrix and tuning curve
    cm_path = "plots/fig6_confusion_matrix.png"
    if os.path.exists(cm_path):
        s5.shapes.add_picture(cm_path, Inches(0.8), Inches(1.5), Inches(4.8))

    tune_path = "plots/fig7_hyperparameter_tuning.png"
    if os.path.exists(tune_path):
        s5.shapes.add_picture(tune_path, Inches(5.9), Inches(1.5), Inches(6.6))

    # Bottom summary bar
    sum_bar = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.3))
    sum_bar.fill.solid()
    sum_bar.fill.fore_color.rgb = RGBColor(232, 245, 233) # light green
    sum_bar.line.color.rgb = RGBColor(76, 175, 80)
    tb_sb = s5.shapes.add_textbox(Inches(1.0), Inches(5.65), Inches(11.333), Inches(1.2))
    tfsb = tb_sb.text_frame
    tfsb.word_wrap = True

    p = tfsb.paragraphs[0]
    p.text = "Key Performance Highlights:"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(27, 94, 32)
    p.space_after = Pt(3)

    p2 = tfsb.add_paragraph()
    p2.text = "• Test Set Accuracy: 100.00% across all 82 held-out samples (16 2psc, 16 3psc, 34 no fault, 16 spgf) with zero errors.\n" \
              "• Baseline Comparison: Random Forest (100.00%) and K-Nearest Neighbors (100.00%) confirm strong class separability.\n" \
              "• Advantage of SVM: Lowest computational overhead, zero risk of overfitting, and convex optimization guarantee."
    p2.font.name = "Calibri"
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_DARK

    # =============================================================
    # SLIDE 6: Final Analysis: How the Model Works (Exactly)
    # =============================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Final Analysis: How the Protection Model Works (Step-by-Step)", "MODEL INFERENCE ENGINE & RELAY LOGIC")

    # 3 Column Cards
    col_w = Inches(3.68)
    col_gap = Inches(0.34)

    # Col 1: Step 1 - Input Sensing & Normalization
    c1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), col_w, Inches(4.3))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = BORDER_COLOR
    tb_c1 = s6.shapes.add_textbox(Inches(0.95), Inches(1.65), col_w - Inches(0.3), Inches(4.0))
    t1 = tb_c1.text_frame
    t1.word_wrap = True
    p = t1.paragraphs[0]
    p.text = "1. Input & Normalization"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    pts1 = [
        "Sensor Vector (x): Ingests 24 continuous measurements (9 PT voltages Ua1-Uc3 in kV + 15 CT currents Ia1-Ic5 in kA).",
        "Z-Score Standardization: Normalizes each input feature using pre-saved training parameters:",
        "zⱼ = (xⱼ - μⱼ) / σⱼ",
        "Why it matters: Prevents high voltages (~63.5 kV) from overpowering smaller currents (~0.2 kA), giving equal mathematical weight to all sensors."
    ]
    for idx, b in enumerate(pts1):
        p = t1.add_paragraph()
        if idx == 2:
            p.text = b
            p.font.name = "Consolas"
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = RGBColor(15, 76, 129)
        else:
            p.text = "• " + b
            p.font.name = "Calibri"
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # Col 2: Step 2 - SVM Hyperplane Decision Engine
    c2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8) + col_w + col_gap, Inches(1.5), col_w, Inches(4.3))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG
    c2.line.color.rgb = BORDER_COLOR
    tb_c2 = s6.shapes.add_textbox(Inches(0.95) + col_w + col_gap, Inches(1.65), col_w - Inches(0.3), Inches(4.0))
    t2 = tb_c2.text_frame
    t2.word_wrap = True
    p = t2.paragraphs[0]
    p.text = "2. SVM Decision Engine"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    pts2 = [
        "Hyperplane Function: Evaluates the optimal maximum-margin boundary:",
        "f(z) = sign(wᵀ z + b)",
        "One-vs-One (OvO) Voting: Evaluates 6 pairwise binary classifiers across the 4 classes (2psc, 3psc, no fault, spgf).",
        "Probability Calibration: Platt scaling computes posterior probabilities (e.g. 98.3% - 99.9% confidence).",
        "Physical Boundary: Separates balanced zero-sequence (spgf), negative-sequence (2psc), and symmetric sag (3psc)."
    ]
    for idx, b in enumerate(pts2):
        p = t2.add_paragraph()
        if idx == 1:
            p.text = b
            p.font.name = "Consolas"
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = RGBColor(15, 76, 129)
        else:
            p.text = "• " + b
            p.font.name = "Calibri"
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # Col 3: Step 3 - Digital Relay Trip Decision
    c3 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8) + 2*(col_w + col_gap), Inches(1.5), col_w, Inches(4.3))
    c3.fill.solid()
    c3.fill.fore_color.rgb = CARD_BG
    c3.line.color.rgb = BORDER_COLOR
    tb_c3 = s6.shapes.add_textbox(Inches(0.95) + 2*(col_w + col_gap), Inches(1.65), col_w - Inches(0.3), Inches(4.0))
    t3 = tb_c3.text_frame
    t3.word_wrap = True
    p = t3.paragraphs[0]
    p.text = "3. Relay Action Logic"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    pts3 = [
        "Decision Rule Mapping:",
        "'no fault': Maintain CLOSED breakers (power transfer continues uninterrupted).",
        "'spgf': Issue SINGLE-POLE TRIP on faulted phase only; auto-reclose preserves grid synchronism on 2 healthy phases.",
        "'2psc' / '3psc': Issue THREE-POLE TRIP & LOCKOUT immediately to isolate high-energy multiphase short circuits."
    ]
    for b in pts3:
        p = t3.add_paragraph()
        p.text = "• " + b
        p.font.name = "Calibri"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # Bottom Full-Width Banner: Execution Speed & Protection Feasibility
    bot_bar = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.733), Inches(1.1))
    bot_bar.fill.solid()
    bot_bar.fill.fore_color.rgb = RGBColor(232, 245, 233) # light green
    bot_bar.line.color.rgb = RGBColor(76, 175, 80)
    tb_bb = s6.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(11.333), Inches(1.0))
    tfbb = tb_bb.text_frame
    tfbb.word_wrap = True

    p_bb = tfbb.paragraphs[0]
    p_bb.text = "Sub-Cycle Real-Time Protection Benchmark:"
    p_bb.font.name = "Calibri"
    p_bb.font.size = Pt(12)
    p_bb.font.bold = True
    p_bb.font.color.rgb = RGBColor(27, 94, 32)
    p_bb.space_after = Pt(2)

    p_bb2 = tfbb.add_paragraph()
    p_bb2.text = "• Measured Inference Speed: 0.302 ms (302 μs) per prediction across 1,000 runs.\n" \
                 "• In a 50 Hz power system (1 cycle = 20.0 ms), inference consumes only 1.51% of one power cycle, leaving > 98% of the cycle for DFT phasor calculation and physical breaker trip travel."
    p_bb2.font.name = "Calibri"
    p_bb2.font.size = Pt(10.5)
    p_bb2.font.color.rgb = TEXT_DARK

    # Save
    out_ppt = "ESA_Project15_Fault_Classification_Presentation.pptx"
    prs.save(out_ppt)
    print(f"Presentation saved successfully to: {out_ppt}")

if __name__ == '__main__':
    create_deck()

