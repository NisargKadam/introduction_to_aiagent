/**
 * script.js - Client-side logic for the Multi-Pattern AI Agent Demo
 *
 * Dynamically renders graph topologies for 4 agent patterns and
 * processes SSE events to animate node execution in real-time.
 */

// ─── DOM References ───
const promptInput      = document.getElementById("prompt");
const runBtn           = document.getElementById("run-btn");
const outputSection    = document.getElementById("output-section");
const outputLog        = document.getElementById("output-log");
const modelSelect      = document.getElementById("model-select");
const modelBadge       = document.getElementById("model-badge");
const patternSelect    = document.getElementById("pattern-select");
const patternBadge     = document.getElementById("pattern-badge");
const patternDesc      = document.getElementById("pattern-description");
const graphContainer   = document.getElementById("graph-container");

let currentPattern = "sequential";

// Allow pressing Enter to run
promptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runAgent();
});


// ─── Graph Topologies ───
// Each pattern defines its nodes, edges, and layout type for rendering.

const GRAPH_TOPOLOGIES = {
    sequential: {
        layout: "linear",
        nodes: [
            { id: "input",         label: "User Input",         icon: "IN" },
            { id: "reason_node",   label: "Reason Node",        icon: "1" },
            { id: "tool_node",     label: "Tool Decision Node",  icon: "2" },
            { id: "response_node", label: "Response Node",       icon: "3" },
            { id: "end",           label: "END",                 icon: null, isEnd: true },
        ],
    },
    branching: {
        layout: "branching",
        nodes: [
            { id: "input",     label: "User Input",      icon: "IN" },
            { id: "classify",  label: "Classify (Router)", icon: "1" },
        ],
        branches: [
            { id: "technical", label: "Technical",   icon: "T" },
            { id: "creative",  label: "Creative",    icon: "C" },
            { id: "factual",   label: "Factual",     icon: "F" },
        ],
        after: [
            { id: "merge", label: "Merge",  icon: "M" },
            { id: "end",   label: "END",    icon: null, isEnd: true },
        ],
    },
    parallel: {
        layout: "parallel",
        nodes: [
            { id: "input", label: "User Input", icon: "IN" },
        ],
        parallel: [
            { id: "analyst_technical",  label: "Technical Analyst",  icon: "T" },
            { id: "analyst_practical",  label: "Practical Analyst",  icon: "P" },
            { id: "analyst_beginner",   label: "Beginner Analyst",   icon: "B" },
        ],
        after: [
            { id: "synthesize", label: "Synthesize", icon: "S" },
            { id: "end",        label: "END",        icon: null, isEnd: true },
        ],
    },
    loop: {
        layout: "loop",
        nodes: [
            { id: "input",    label: "User Input", icon: "IN" },
            { id: "draft",    label: "Draft",       icon: "D" },
            { id: "critique", label: "Critique",    icon: "C" },
            { id: "finalize", label: "Finalize",    icon: "F" },
            { id: "end",      label: "END",         icon: null, isEnd: true },
        ],
    },
};


// ─── Graph Renderer ───

function renderGraph(pattern) {
    const topo = GRAPH_TOPOLOGIES[pattern];
    if (!topo) return;

    graphContainer.innerHTML = "";
    graphContainer.className = `graph graph-${topo.layout}`;

    if (topo.layout === "linear") {
        topo.nodes.forEach((node, i) => {
            graphContainer.appendChild(createNodeBox(node));
            if (i < topo.nodes.length - 1) {
                graphContainer.appendChild(createArrow());
            }
        });
    }

    else if (topo.layout === "branching") {
        // Pre-branch nodes
        topo.nodes.forEach((node) => {
            graphContainer.appendChild(createNodeBox(node));
            graphContainer.appendChild(createArrow());
        });

        // Branch label
        const branchLabel = document.createElement("div");
        branchLabel.className = "branch-label";
        branchLabel.textContent = "Conditional Route (one branch executes)";
        graphContainer.appendChild(branchLabel);

        // Branch row
        const row = document.createElement("div");
        row.className = "branch-row";
        topo.branches.forEach((node) => {
            row.appendChild(createNodeBox(node));
        });
        graphContainer.appendChild(row);

        // After-branch
        graphContainer.appendChild(createArrow());
        topo.after.forEach((node, i) => {
            graphContainer.appendChild(createNodeBox(node));
            if (i < topo.after.length - 1) {
                graphContainer.appendChild(createArrow());
            }
        });
    }

    else if (topo.layout === "parallel") {
        // Input node
        topo.nodes.forEach((node) => {
            graphContainer.appendChild(createNodeBox(node));
            graphContainer.appendChild(createArrow());
        });

        // Parallel label
        const parLabel = document.createElement("div");
        parLabel.className = "parallel-label";
        parLabel.textContent = "Parallel Superstep (all run concurrently)";
        graphContainer.appendChild(parLabel);

        // Parallel row
        const row = document.createElement("div");
        row.className = "parallel-row";
        topo.parallel.forEach((node) => {
            row.appendChild(createNodeBox(node));
        });
        graphContainer.appendChild(row);

        // After-parallel
        graphContainer.appendChild(createArrow());
        topo.after.forEach((node, i) => {
            graphContainer.appendChild(createNodeBox(node));
            if (i < topo.after.length - 1) {
                graphContainer.appendChild(createArrow());
            }
        });
    }

    else if (topo.layout === "loop") {
        // Input
        graphContainer.appendChild(createNodeBox(topo.nodes[0]));
        graphContainer.appendChild(createArrow());

        // Loop container with back-arrow
        const loopWrap = document.createElement("div");
        loopWrap.className = "loop-container";

        const loopNodes = document.createElement("div");
        loopNodes.className = "loop-nodes";

        // Draft node
        loopNodes.appendChild(createNodeBox(topo.nodes[1]));
        loopNodes.appendChild(createArrow());
        // Critique node
        loopNodes.appendChild(createNodeBox(topo.nodes[2]));

        loopWrap.appendChild(loopNodes);

        // Loop-back arrow
        const loopArrow = document.createElement("div");
        loopArrow.className = "loop-arrow";
        loopArrow.innerHTML = '<div class="loop-arrow-line"></div><div class="loop-arrow-label">Loop back if NEEDS_WORK</div>';
        loopWrap.appendChild(loopArrow);

        graphContainer.appendChild(loopWrap);

        // Arrow to finalize
        graphContainer.appendChild(createArrow());
        const arrowLabel = document.createElement("div");
        arrowLabel.className = "arrow-label";
        arrowLabel.textContent = "APPROVED";
        graphContainer.appendChild(arrowLabel);

        // Finalize + END
        graphContainer.appendChild(createNodeBox(topo.nodes[3]));
        graphContainer.appendChild(createArrow());
        graphContainer.appendChild(createNodeBox(topo.nodes[4]));
    }
}

function createNodeBox(node) {
    const box = document.createElement("div");
    box.className = `node-box${node.isEnd ? " node-end" : ""}`;
    box.id = `node-${node.id}`;

    if (node.icon) {
        const icon = document.createElement("span");
        icon.className = "node-icon";
        icon.textContent = node.icon;
        box.appendChild(icon);
    }

    const label = document.createElement("span");
    label.className = "node-label";
    label.textContent = node.label;
    box.appendChild(label);

    if (!node.isEnd && node.id !== "input") {
        const status = document.createElement("span");
        status.className = "node-status";
        status.id = `status-${node.id}`;
        box.appendChild(status);
    }

    return box;
}

function createArrow() {
    const arrow = document.createElement("div");
    arrow.className = "arrow";
    arrow.innerHTML = "&#x2193;";
    return arrow;
}


// ─── Main Run Function ───

async function runAgent() {
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    resetUI();
    runBtn.disabled = true;
    runBtn.textContent = "Running...";
    outputSection.classList.add("visible");

    // Highlight the input node
    const inputNode = document.getElementById("node-input");
    if (inputNode) inputNode.classList.add("completed");

    try {
        const response = await fetch("/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split("\n\n");
            buffer = parts.pop();

            for (const part of parts) {
                processSSE(part);
            }
        }

        if (buffer.trim()) {
            processSSE(buffer);
        }
    } catch (err) {
        appendLog("Error", err.message, "error");
    }

    runBtn.disabled = false;
    runBtn.textContent = "Run Agent";
}


// ─── SSE Event Processor (Generic) ───

function processSSE(raw) {
    const lines = raw.trim().split("\n");
    let eventType = "";
    let data = {};

    for (const line of lines) {
        if (line.startsWith("event: ")) {
            eventType = line.slice(7);
        } else if (line.startsWith("data: ")) {
            try {
                data = JSON.parse(line.slice(6));
            } catch { /* skip malformed */ }
        }
    }

    if (!eventType) return;

    switch (eventType) {
        case "pattern_info": {
            // Pattern confirmed by server
            break;
        }

        case "node_start": {
            const nodeEl = document.getElementById(`node-${data.node}`);
            if (nodeEl) {
                nodeEl.classList.add("active");
                const statusEl = document.getElementById(`status-${data.node}`);
                if (statusEl) statusEl.textContent = data.label;
            }
            break;
        }

        case "node_complete": {
            const nodeEl = document.getElementById(`node-${data.node}`);
            if (nodeEl) {
                nodeEl.classList.remove("active");
                nodeEl.classList.add("completed");
                const statusEl = document.getElementById(`status-${data.node}`);
                if (statusEl) statusEl.textContent = "Done";
            }

            // For branching: dim unchosen branches
            if (currentPattern === "branching" && data.node === "classify" && data.state && data.state.route) {
                const route = data.state.route;
                const branches = ["technical", "creative", "factual"];
                branches.forEach((b) => {
                    if (b !== route) {
                        const el = document.getElementById(`node-${b}`);
                        if (el) el.classList.add("dimmed");
                    }
                });
            }

            // Append to execution log
            const logTitle = data.node.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
            const cssClass = getLogClass(data.node);
            appendLog(logTitle, data.output || "", cssClass);
            break;
        }

        case "done": {
            const endNode = document.getElementById("node-end");
            if (endNode) endNode.classList.add("completed");
            break;
        }
    }
}

function getLogClass(nodeName) {
    // Map node names to CSS color classes
    const map = {
        reason_node: "reason", tool_node: "tool", response_node: "response",
        classify: "reason", technical: "tool", creative: "creative-log", factual: "response", merge: "response",
        analyst_technical: "reason", analyst_practical: "tool", analyst_beginner: "creative-log", synthesize: "response",
        draft: "reason", critique: "tool", finalize: "response",
    };
    return map[nodeName] || "reason";
}


// ─── Helpers ───

function appendLog(title, text, cssClass) {
    const entry = document.createElement("div");
    entry.className = `log-entry ${cssClass}`;
    entry.innerHTML = `
        <div class="log-title">${title}</div>
        <div class="log-text">${escapeHtml(text)}</div>
    `;
    outputLog.appendChild(entry);
    entry.scrollIntoView({ behavior: "smooth", block: "end" });
}

function resetUI() {
    document.querySelectorAll(".node-box").forEach((el) => {
        el.classList.remove("active", "completed", "dimmed");
    });
    document.querySelectorAll(".node-status").forEach((el) => {
        el.textContent = "";
    });
    outputLog.innerHTML = "";
}

function setPrompt(text) {
    promptInput.value = text;
    promptInput.focus();
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


// ─── Pattern Selector ───

async function loadPatterns() {
    try {
        const res = await fetch("/patterns");
        const data = await res.json();

        patternSelect.innerHTML = "";
        for (const [key, info] of Object.entries(data.patterns)) {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = info.name;
            if (key === data.current) opt.selected = true;
            patternSelect.appendChild(opt);
        }

        currentPattern = data.current;
        const currentInfo = data.patterns[data.current];
        patternBadge.textContent = currentInfo.name;
        patternDesc.textContent = currentInfo.description;
        renderGraph(currentPattern);
    } catch {
        patternSelect.innerHTML = "<option>Error loading</option>";
    }
}

async function changePattern(pattern) {
    try {
        const res = await fetch("/set-pattern", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pattern }),
        });
        const data = await res.json();
        currentPattern = data.current;

        // Update badge and description
        const patternRes = await fetch("/patterns");
        const patternData = await patternRes.json();
        const info = patternData.patterns[currentPattern];
        patternBadge.textContent = info.name;
        patternDesc.textContent = info.description;

        // Re-render graph
        renderGraph(currentPattern);

        // Reset output
        outputSection.classList.remove("visible");
        outputLog.innerHTML = "";
    } catch {
        patternBadge.textContent = "Error";
    }
}


// ─── Model Selector ───

async function loadModels() {
    try {
        const res = await fetch("/models");
        const data = await res.json();

        modelSelect.innerHTML = "";
        for (const model of data.models) {
            const opt = document.createElement("option");
            opt.value = model;
            opt.textContent = model;
            if (model === data.current) opt.selected = true;
            modelSelect.appendChild(opt);
        }
        modelBadge.textContent = data.current;
    } catch {
        modelSelect.innerHTML = "<option>Error loading</option>";
    }
}

async function changeModel(model) {
    try {
        const res = await fetch("/set-model", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model }),
        });
        const data = await res.json();
        modelBadge.textContent = data.current;
    } catch {
        modelBadge.textContent = "Error";
    }
}


// ─── Fine-Tuning Panel ───

const tuningSection = document.getElementById("tuning-section");
const tuneToggle    = document.getElementById("tune-toggle");

function toggleTuning() {
    const isVisible = tuningSection.classList.toggle("visible");
    tuneToggle.classList.toggle("active", isVisible);
}

function updateSlider(param, value) {
    document.getElementById(`val-${param}`).textContent = value;
    sendParam(param, parseFloat(value));
}

async function sendParam(param, value) {
    const payload = {};
    payload[param] = param === "max_tokens" ? parseInt(value) : value;
    try {
        await fetch("/set-params", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    } catch { /* silently fail */ }
}

async function loadParams() {
    try {
        const res = await fetch("/params");
        const data = await res.json();
        setSlider("tune-temperature", "temperature", data.temperature);
        setSlider("tune-max-tokens", "max_tokens", data.max_tokens);
        setSlider("tune-top-p", "top_p", data.top_p);
        setSlider("tune-freq", "frequency_penalty", data.frequency_penalty);
        setSlider("tune-pres", "presence_penalty", data.presence_penalty);
    } catch { /* use defaults */ }
}

function setSlider(sliderId, param, value) {
    const slider = document.getElementById(sliderId);
    if (slider) slider.value = value;
    const display = document.getElementById(`val-${param}`);
    if (display) display.textContent = value;
}

const PRESETS = {
    precise:  { temperature: 0.2, max_tokens: 200, top_p: 0.5, frequency_penalty: 0.0, presence_penalty: 0.0 },
    balanced: { temperature: 0.7, max_tokens: 300, top_p: 0.9, frequency_penalty: 0.3, presence_penalty: 0.2 },
    creative: { temperature: 1.2, max_tokens: 500, top_p: 1.0, frequency_penalty: 0.5, presence_penalty: 0.5 },
};

async function applyPreset(name) {
    const preset = PRESETS[name];
    if (!preset) return;
    setSlider("tune-temperature", "temperature", preset.temperature);
    setSlider("tune-max-tokens", "max_tokens", preset.max_tokens);
    setSlider("tune-top-p", "top_p", preset.top_p);
    setSlider("tune-freq", "frequency_penalty", preset.frequency_penalty);
    setSlider("tune-pres", "presence_penalty", preset.presence_penalty);
    try {
        await fetch("/set-params", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(preset),
        });
    } catch { /* silently fail */ }
}


// ─── Initialize on page load ───
loadPatterns();
loadModels();
loadParams();
