const dashboard = document.getElementById("dashboard");
const toggleDashboard = document.getElementById("toggle-dashboard");
const spotlightModal = document.getElementById("spotlight-modal");
const openSpotlight = document.getElementById("open-spotlight");
const closeSpotlight = document.getElementById("close-spotlight");
const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".tab-panel");
const cards = document.querySelectorAll(".card[data-panel]");
const pulseBar = document.getElementById("pulse-bar");
const seatCount = document.getElementById("seat-count");
const issuePass = document.getElementById("issue-pass");
const passHint = document.getElementById("pass-hint");

function activateTab(targetId) {
  panels.forEach((panel) => panel.classList.remove("active"));
  tabs.forEach((tab) => tab.classList.remove("active"));
  const panel = document.getElementById(targetId);
  const tab = document.querySelector(`[data-tab="${targetId}"]`);
  if (panel && tab) {
    panel.classList.add("active");
    tab.classList.add("active");
  }
}

if (toggleDashboard && dashboard) {
  toggleDashboard.addEventListener("click", () => {
    dashboard.classList.toggle("active");
    dashboard.style.display = dashboard.classList.contains("active") ? "block" : "none";
  });
}

if (openSpotlight) {
  openSpotlight.addEventListener("click", () => {
    spotlightModal.classList.add("active");
  });
}

if (closeSpotlight) {
  closeSpotlight.addEventListener("click", () => {
    spotlightModal.classList.remove("active");
  });
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => activateTab(tab.dataset.tab));
});

cards.forEach((card) => {
  card.addEventListener("click", () => {
    const target = card.dataset.panel;
    if (target) {
      activateTab("tab-one");
      dashboard.classList.add("active");
      dashboard.style.display = "block";
      const targetPanel = document.getElementById(target);
      if (targetPanel) {
        targetPanel.scrollIntoView({ behavior: "smooth", block: "center" });
        targetPanel.classList.add("highlight");
        setTimeout(() => targetPanel.classList.remove("highlight"), 900);
      }
    }
  });
});

const refreshPulse = document.getElementById("refresh-pulse");
if (refreshPulse && pulseBar) {
  refreshPulse.addEventListener("click", () => {
    const value = 20 + Math.floor(Math.random() * 70);
    pulseBar.style.width = `${value}%`;
  });
}

if (seatCount) {
  const base = 160;
  setInterval(() => {
    const delta = Math.floor(Math.random() * 30);
    seatCount.textContent = `${base + delta} available`;
  }, 3500);
}

if (issuePass) {
  issuePass.addEventListener("click", () => {
    if (passHint) {
      passHint.textContent = "Pass queued. Please check email for pickup.";
    }
  });
}

const checklistBtn = document.getElementById("complete-checklist");
if (checklistBtn) {
  checklistBtn.addEventListener("click", () => {
    showClickNotice();
  });
}

function ensureToast() {
  let toast = document.getElementById("stateeye-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "stateeye-toast";
    toast.style.position = "fixed";
    toast.style.right = "24px";
    toast.style.bottom = "24px";
    toast.style.background = "#10212b";
    toast.style.color = "#fff";
    toast.style.padding = "10px 16px";
    toast.style.borderRadius = "999px";
    toast.style.fontSize = "0.9rem";
    toast.style.boxShadow = "0 12px 24px rgba(16,33,43,0.2)";
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.2s ease";
    document.body.appendChild(toast);
  }
  return toast;
}

function showClickNotice() {
  const toast = ensureToast();
  toast.textContent = "Button clicked";
  toast.style.opacity = "1";
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.style.opacity = "0";
  }, 1400);
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) {
    return;
  }
  showClickNotice();
});
