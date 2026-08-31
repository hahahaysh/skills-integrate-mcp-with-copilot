document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const adminToggle = document.getElementById("admin-toggle");
  const adminLoginModal = document.getElementById("admin-login-modal");
  const closeLoginModal = document.getElementById("close-login-modal");
  const adminLoginForm = document.getElementById("admin-login-form");
  const adminPanel = document.getElementById("admin-panel");
  const adminStatus = document.getElementById("admin-status");
  const adminActivityForm = document.getElementById("admin-activity-form");
  const adminLogout = document.getElementById("admin-logout");
  const categoryFilter = document.getElementById("category-filter");
  const searchFilter = document.getElementById("search-filter");
  const sortFilter = document.getElementById("sort-filter");

  const token = () => localStorage.getItem("teacherToken");

  function showMessage(text, type = "success") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  function updateAdminUI() {
    const currentToken = token();
    const username = localStorage.getItem("teacherUsername");

    if (currentToken) {
      adminPanel.classList.remove("hidden");
      adminStatus.textContent = `Logged in as ${username || "teacher"}`;
    } else {
      adminPanel.classList.add("hidden");
      adminStatus.textContent = "Not signed in";
    }
  }

  function openAdminModal() {
    adminLoginModal.classList.remove("hidden");
    adminLoginModal.setAttribute("aria-hidden", "false");
  }

  function closeAdminModal() {
    adminLoginModal.classList.add("hidden");
    adminLoginModal.setAttribute("aria-hidden", "true");
  }

  function populateCategoryFilter(activities) {
    const categories = new Set();
    Object.values(activities).forEach((activity) => {
      if (activity.category) {
        categories.add(activity.category);
      }
    });

    const currentValue = categoryFilter.value;
    categoryFilter.innerHTML = '<option value="">All</option>';
    [...categories].sort().forEach((category) => {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categoryFilter.appendChild(option);
    });
    categoryFilter.value = currentValue || "";
  }

  async function fetchActivities() {
    try {
      const params = new URLSearchParams();
      const selectedCategory = categoryFilter.value;
      const searchTerm = searchFilter.value.trim();
      const sortValue = sortFilter.value;

      if (selectedCategory) params.set("category", selectedCategory);
      if (searchTerm) params.set("search", searchTerm);
      if (sortValue) params.set("sort", sortValue);

      const query = params.toString();
      const response = await fetch(`/activities${query ? `?${query}` : ""}`);
      const activities = await response.json();
      const items = Array.isArray(activities)
        ? activities
        : Object.entries(activities).map(([name, details]) => ({ name, ...details }));

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      if (!items.length) {
        activitiesList.innerHTML = "<p>No activities match your filters.</p>";
        return;
      }

      if (!Array.isArray(activities)) {
        populateCategoryFilter(activities);
      }

      items.forEach((item) => {
        const name = item.name;
        const details = item;
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <div class="activity-meta">
            <span class="activity-category">${details.category || "General"}</span>
            <span class="activity-date">${details.date || "No date"}</span>
          </div>
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  adminToggle.addEventListener("click", () => {
    if (token()) {
      updateAdminUI();
      return;
    }
    openAdminModal();
  });

  closeLoginModal.addEventListener("click", closeAdminModal);

  adminLoginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("admin-username").value;
    const password = document.getElementById("admin-password").value;

    try {
      const response = await fetch("/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const result = await response.json();

      if (response.ok) {
        localStorage.setItem("teacherToken", result.token);
        localStorage.setItem("teacherUsername", result.username);
        closeAdminModal();
        adminLoginForm.reset();
        updateAdminUI();
        showMessage(`Logged in as ${result.username}`, "success");
      } else {
        showMessage(result.detail || "Login failed", "error");
      }
    } catch (error) {
      showMessage("Failed to log in. Please try again.", "error");
      console.error("Error logging in:", error);
    }
  });

  adminActivityForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      name: document.getElementById("admin-activity-name").value,
      description: document.getElementById("admin-activity-description").value,
      schedule: document.getElementById("admin-activity-schedule").value,
      max_participants: Number(document.getElementById("admin-activity-capacity").value),
    };

    try {
      const response = await fetch("/admin/activities", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (response.ok) {
        adminActivityForm.reset();
        fetchActivities();
        showMessage(`${result.name} was created successfully.`, "success");
      } else {
        showMessage(result.detail || "Could not create activity.", "error");
      }
    } catch (error) {
      showMessage("Failed to create activity.", "error");
      console.error("Error creating activity:", error);
    }
  });

  adminLogout.addEventListener("click", () => {
    localStorage.removeItem("teacherToken");
    localStorage.removeItem("teacherUsername");
    updateAdminUI();
    showMessage("Logged out successfully.", "info");
  });

  categoryFilter.addEventListener("change", fetchActivities);
  searchFilter.addEventListener("input", fetchActivities);
  sortFilter.addEventListener("change", fetchActivities);

  updateAdminUI();
  fetchActivities();
});
