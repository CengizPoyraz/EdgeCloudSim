#!/usr/bin/env python3
"""
Generate Academic PDF Report for Energy-Aware Task Offloading Study
"""

import os
from fpdf import FPDF

script_dir = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(script_dir, "..", "figures")
OUTPUT_DIR = os.path.join(script_dir, "..", "output")

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(128)
            self.cell(0, 8, 'Energy-Aware Task Offloading in Edge Computing', align='C')
            self.ln(10)
            
    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
        
    def title_page(self):
        self.add_page()
        self.ln(50)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 51, 102)
        self.multi_cell(0, 12, 'Energy-Aware Task Offloading\nwith Deadline Constraints\nin Edge Computing', align='C')
        self.ln(15)
        self.set_font('Helvetica', 'I', 14)
        self.set_text_color(64)
        self.cell(0, 10, 'A Simulation Study Using EdgeCloudSim Framework', align='C')
        self.ln(30)
        self.set_font('Helvetica', '', 12)
        self.set_text_color(0)
        self.cell(0, 8, 'Cengiz Poyraz', align='C')
        self.ln(8)
        self.cell(0, 8, 'CMPE 583 - Edge Computing', align='C')
        
    def section_title(self, title, num=None):
        self.ln(3)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 51, 102)
        if num:
            self.cell(0, 8, f'{num}. {title}', ln=True)
        else:
            self.cell(0, 8, title, ln=True)
        self.ln(1)
        self.set_text_color(0)
        
    def subsection_title(self, title, num=None):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(51, 51, 51)
        if num:
            self.cell(0, 6, f'{num} {title}', ln=True)
        else:
            self.cell(0, 6, title, ln=True)
        self.set_text_color(0)
        
    def body_text(self, text):
        self.set_font('Helvetica', '', 9)
        self.multi_cell(0, 4.5, text)
        self.ln(1)
        
    def add_figure(self, img_path, caption, width=140):
        if os.path.exists(img_path):
            if self.get_y() > 200:
                self.add_page()
            x = (210 - width) / 2
            self.image(img_path, x=x, w=width)
            self.ln(2)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(64)
            self.multi_cell(0, 4, caption, align='C')
            self.set_text_color(0)
            self.ln(3)
        else:
            self.body_text(f"[Figure not found: {img_path}]")

def create_report():
    pdf = ReportPDF()
    
    pdf.title_page()
    
    pdf.add_page()
    pdf.section_title('Abstract')
    pdf.body_text(
        "This report presents an energy-aware task offloading algorithm (EADC) for edge computing environments "
        "that balances mobile device energy consumption with application deadline satisfaction. Edge computing "
        "enables mobile devices to offload computational tasks to nearby edge servers, reducing local processing "
        "burden. However, deciding when and where to offload requires careful consideration of energy costs, "
        "network delays, and deadline constraints. We implement and evaluate the EADC algorithm against four "
        "competitor strategies using the EdgeCloudSim simulation framework. Results demonstrate that EADC "
        "achieves superior deadline satisfaction rates while maintaining competitive energy efficiency, "
        "particularly for delay-sensitive applications like augmented reality and interactive gaming."
    )
    
    pdf.section_title('Introduction', 1)
    pdf.body_text(
        "Mobile devices have become essential computing platforms, but their limited battery capacity constrains "
        "the execution of computationally intensive applications. Edge computing addresses this challenge by "
        "deploying servers at the network edge, closer to end users than traditional cloud datacenters. This "
        "proximity enables lower latency and reduced energy consumption for mobile devices that offload tasks "
        "to edge servers."
    )
    pdf.body_text(
        "However, task offloading decisions are non-trivial. Offloading saves mobile device energy but incurs "
        "network transmission costs and may introduce delays if edge servers are congested. For time-sensitive "
        "applications such as augmented reality (AR), virtual reality (VR), and interactive gaming, missing "
        "deadlines leads to poor user experience. Therefore, an effective offloading strategy must balance "
        "energy efficiency with deadline satisfaction."
    )
    pdf.body_text(
        "This study develops and evaluates the Energy-Aware Deadline-Constrained (EADC) algorithm that considers "
        "both energy consumption and deadline requirements when making offloading decisions. We compare EADC "
        "against four baseline algorithms: Random selection, Greedy-Energy (minimizes energy), Greedy-Deadline "
        "(minimizes response time), and Edge-Only (always offloads to edge)."
    )
    
    pdf.section_title('Problem Statement', 2)
    pdf.body_text(
        "Given a set of mobile devices generating computational tasks with varying characteristics (computation "
        "requirements, data sizes, deadlines), and a set of edge servers with limited processing capacity, the "
        "task offloading problem is to decide for each task whether to: (1) Execute locally on the mobile device, "
        "(2) Offload to an edge server, or (3) Offload to the cloud datacenter."
    )
    pdf.body_text(
        "The objective is to minimize mobile device energy consumption while maximizing the fraction of tasks "
        "that complete before their deadlines. This is a multi-objective optimization problem where the two "
        "goals may conflict: aggressive offloading saves mobile energy but may overload edge servers, causing "
        "deadline violations."
    )
    
    pdf.subsection_title('Application Types', '2.1')
    pdf.body_text(
        "We consider four application types with different characteristics: "
        "Real-time AR/VR (very high delay sensitivity 0.95, tight deadline 80ms, frequent tasks); "
        "Interactive Gaming (high delay sensitivity 0.75, moderate deadline 250ms); "
        "Image Processing (low delay sensitivity 0.35, relaxed deadline 1500ms, large data); "
        "Data Synchronization (very low delay sensitivity 0.15, long deadline 5000ms)."
    )
    
    pdf.section_title('Proposed Algorithm: EADC', 3)
    pdf.body_text(
        "The Energy-Aware Deadline-Constrained (EADC) algorithm makes offloading decisions by evaluating a "
        "utility score for each potential execution location. The algorithm adapts its behavior based on "
        "application delay sensitivity and current edge server load."
    )
    
    pdf.subsection_title('Utility Function', '3.1')
    pdf.body_text(
        "For each task t and execution location l (mobile, edge, or cloud), EADC computes: "
        "Score(t, l) = alpha * (T_l / D_t) + beta * (E_l / E_max) + gamma * LoadPenalty(l). "
        "Where T_l is estimated completion time at location l, D_t is task deadline, E_l is energy consumption, "
        "E_max is maximum possible energy, alpha and beta are weighting factors (alpha + beta = 1), "
        "and gamma is the load penalty coefficient."
    )
    
    pdf.subsection_title('Adaptive Weighting', '3.2')
    pdf.body_text(
        "The weighting factors alpha and beta are adapted based on application delay sensitivity (s): "
        "alpha = 0.3 + 0.5 * s (ranges from 0.3 to 0.8), beta = 1 - alpha (ranges from 0.7 to 0.2). "
        "For delay-sensitive applications (high s), alpha is larger, prioritizing deadline satisfaction. "
        "For delay-tolerant applications (low s), beta is larger, prioritizing energy efficiency."
    )
    
    pdf.subsection_title('Load-Aware Selection', '3.3')
    pdf.body_text(
        "EADC applies a penalty to overloaded edge servers: LoadPenalty = 0.3 * (queue_length / max_queue)^2. "
        "This quadratic penalty discourages task assignment to heavily loaded servers, improving load "
        "balancing and reducing deadline violations due to queuing delays."
    )
    
    pdf.section_title('Competitor Algorithms', 4)
    pdf.body_text("We compare EADC against four baseline strategies:")
    pdf.body_text(
        "- Random: Randomly selects between mobile, edge, and cloud with equal probability, providing a baseline.\n"
        "- Greedy-Energy: Always selects the execution location that minimizes energy consumption, without considering deadlines.\n"
        "- Greedy-Deadline: Always selects the execution location that minimizes response time, without considering energy.\n"
        "- Edge-Only: Always offloads to edge servers, a simple strategy that works well under light load but may cause congestion."
    )
    
    pdf.section_title('Simulation Setup', 5)
    
    pdf.subsection_title('Simulation Environment', '5.1')
    pdf.body_text(
        "We implemented the simulation using EdgeCloudSim, a framework built on CloudSim that provides "
        "modeling capabilities for edge computing scenarios. The simulation includes: "
        "5 edge servers with 8000 MIPS processing capacity each, 1 cloud datacenter with 20000 MIPS capacity, "
        "mobile devices with 500 MIPS local processing, WLAN bandwidth of 50 Mbps, WAN bandwidth of 20 Mbps, "
        "WAN propagation delay of 80ms, and simulation duration of 300 seconds with 30-second warm-up period."
    )
    
    pdf.subsection_title('Experimental Design', '5.2')
    pdf.body_text(
        "We vary the number of mobile devices from 100 to 500 in increments of 100 to evaluate algorithm "
        "performance under different load conditions. Each configuration is run 5 times with different "
        "random seeds, and results are averaged. Key performance metrics include: "
        "Deadline Satisfaction Rate (percentage of tasks completing before deadline), "
        "Energy Consumption (average energy per task in Joules), "
        "Service Time (average task completion time in ms), "
        "Edge Utilization (average edge server utilization percentage), and "
        "Failed Task Rate (percentage of tasks that fail)."
    )
    
    pdf.section_title('Results and Analysis', 6)
    
    pdf.subsection_title('Overall Performance Comparison', '6.1')
    fig_path = os.path.join(FIGURES_DIR, "comparison_bar.png")
    pdf.add_figure(fig_path, "Figure 1: Overall performance comparison across all algorithms at 300 devices", 150)
    pdf.body_text(
        "Figure 1 shows the normalized performance comparison across all metrics. EADC achieves the best "
        "balance between deadline satisfaction and energy efficiency. While Greedy-Deadline achieves "
        "slightly higher deadline rates, it consumes significantly more energy. Greedy-Energy saves energy "
        "but at the cost of deadline satisfaction."
    )
    
    pdf.subsection_title('Deadline Satisfaction Analysis', '6.2')
    fig_path = os.path.join(FIGURES_DIR, "deadline_satisfaction.png")
    pdf.add_figure(fig_path, "Figure 2: Deadline satisfaction rate vs. number of mobile devices", 140)
    pdf.body_text(
        "Figure 2 shows deadline satisfaction rates as the number of devices increases. All algorithms "
        "show declining performance under higher load due to increased edge server congestion. EADC "
        "maintains superior deadline satisfaction through adaptive weighting and load-aware server "
        "selection. The Random policy performs worst due to its inability to consider task requirements."
    )
    
    pdf.subsection_title('Energy Consumption Analysis', '6.3')
    fig_path = os.path.join(FIGURES_DIR, "energy_consumption.png")
    pdf.add_figure(fig_path, "Figure 3: Average energy consumption per task vs. number of devices", 140)
    pdf.body_text(
        "Figure 3 shows energy consumption patterns. Greedy-Energy achieves the lowest energy consumption "
        "by always selecting the most energy-efficient option. However, this comes at the cost of deadline "
        "satisfaction. EADC achieves competitive energy efficiency while maintaining better deadline "
        "performance through its adaptive weighting mechanism."
    )
    
    pdf.subsection_title('Service Time Analysis', '6.4')
    fig_path = os.path.join(FIGURES_DIR, "service_time.png")
    pdf.add_figure(fig_path, "Figure 4: Average service time vs. number of devices", 140)
    pdf.body_text(
        "Service times increase with load as edge server queues grow. Greedy-Deadline achieves the lowest "
        "service times by always prioritizing fast execution. EADC maintains reasonable service times "
        "while balancing energy efficiency. Edge-Only shows high service times under heavy load due to "
        "edge server congestion."
    )
    
    pdf.subsection_title('Edge Server Utilization', '6.5')
    fig_path = os.path.join(FIGURES_DIR, "edge_utilization.png")
    pdf.add_figure(fig_path, "Figure 5: Edge server utilization vs. number of devices", 140)
    pdf.body_text(
        "Figure 5 shows edge server utilization patterns. Edge-Only naturally achieves highest utilization "
        "as it always offloads to edge. EADC and other algorithms show moderate utilization, indicating "
        "they make selective offloading decisions based on task characteristics and server load."
    )
    
    pdf.subsection_title('Energy-Deadline Trade-off', '6.6')
    fig_path = os.path.join(FIGURES_DIR, "tradeoff.png")
    pdf.add_figure(fig_path, "Figure 6: Trade-off between energy consumption and deadline satisfaction", 140)
    pdf.body_text(
        "Figure 6 illustrates the fundamental trade-off between energy efficiency and deadline satisfaction. "
        "EADC achieves a favorable position in the trade-off space, offering high deadline satisfaction "
        "with moderate energy consumption. This demonstrates the effectiveness of the adaptive weighting "
        "approach in balancing competing objectives."
    )
    
    pdf.section_title('Discussion', 7)
    pdf.body_text("The experimental results demonstrate several key findings:")
    pdf.body_text(
        "1. Adaptive weighting is effective: EADC's ability to adjust the deadline-energy trade-off based "
        "on application delay sensitivity leads to better overall performance compared to fixed-weight approaches.\n"
        "2. Load awareness prevents congestion: The quadratic load penalty effectively distributes tasks "
        "across edge servers, preventing any single server from becoming a bottleneck.\n"
        "3. Single-objective approaches are suboptimal: Both Greedy-Energy and Greedy-Deadline sacrifice "
        "one objective entirely for the other. Real applications require balanced approaches like EADC.\n"
        "4. Random offloading is insufficient: The Random policy's poor performance highlights the importance "
        "of intelligent offloading decisions in edge computing.\n"
        "5. Scalability challenges: All algorithms show degraded performance under heavy load (500 devices), "
        "suggesting the need for additional edge server capacity or more sophisticated scheduling."
    )
    
    pdf.section_title('Conclusion', 8)
    pdf.body_text(
        "This study presented the Energy-Aware Deadline-Constrained (EADC) algorithm for task offloading in "
        "edge computing environments. Through comprehensive simulation experiments using EdgeCloudSim, we "
        "demonstrated that EADC effectively balances mobile device energy consumption with application "
        "deadline satisfaction. Key contributions include: a utility-based offloading decision framework with "
        "adaptive weighting, load-aware edge server selection to prevent congestion, comprehensive evaluation "
        "against four baseline algorithms, and analysis of the energy-deadline trade-off under varying load "
        "conditions. Future work could extend EADC to consider mobility patterns, heterogeneous edge servers, "
        "and multi-user task dependencies. Additionally, implementing EADC in real edge computing testbeds "
        "would provide valuable validation of the simulation results."
    )
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "assignment_report.pdf")
    pdf.output(output_path)
    print(f"Report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    create_report()
