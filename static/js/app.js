const grid = document.getElementById("propertyGrid");
const emptyState = document.getElementById("emptyState");
const searchForm = document.getElementById("searchForm");

let activeCategory = "All";
let currentProperties = [];

// Set this variable from the Flask template.
const isLoggedIn = window.APP_IS_LOGGED_IN === true;

const money = value =>
  "₹" + Number(value).toLocaleString("en-IN");


async function loadProperties() {
  const params = new URLSearchParams({
    q: document.getElementById("locationInput").value.trim(),
    category: activeCategory,
    sort: document.getElementById("sortSelect")?.value || "recommended"
  });

  try {
    const response = await fetch(`/api/properties?${params}`);

    if (!response.ok) {
      throw new Error("Property request failed");
    }

    currentProperties = await response.json();
    renderProperties(currentProperties);
  } catch (error) {
    grid.innerHTML =
      '<p class="empty-state">Could not load stays. Check that Flask and MySQL are running.</p>';
  }
}


function renderProperties(properties) {
  grid.innerHTML = "";
  emptyState.classList.toggle("hidden", properties.length > 0);

  properties.forEach((p, index) => {
    const card = document.createElement("article");
    card.className = "property-card";

    // The image and title are links to the full details page.
    const detailsUrl = `/property/${p.Property_ID}`;

    card.innerHTML = `
      <div class="photo-wrap">
        <a href="${detailsUrl}" aria-label="View ${p.Property_Name} details">
          <img
            src="${p.Image_URL || ""}"
            alt="${p.Property_Name}"
            loading="lazy"
            onerror="this.style.display='none'; this.parentElement.classList.add('photo-unavailable');"
          >
        </a>

        ${index % 2 === 0
          ? '<span class="guest-badge">Guest favourite</span>'
          : ""}

        <button class="heart" aria-label="Add to favourites"
                title="Add to favourites">♡</button>
      </div>

      <div class="card-info">
        <div class="card-title-row">
          <a class="card-title card-title-link" href="${detailsUrl}">
            ${p.Property_Name}
          </a>
          <span class="rating">★ ${Number(p.Rating || 0).toFixed(1)}</span>
        </div>

        <div class="card-subtitle">
          ${p.Location} · ${p.Category || "Accommodation"}
        </div>

        <div class="card-price">
          <strong>${money(p.Price)}</strong> / night
        </div>

        <div class="card-actions">
          <button class="details-btn" type="button">View details</button>
          <button class="book-btn" type="button">Reserve</button>
        </div>
      </div>
    `;

    card.querySelector(".heart").addEventListener("click", event => {
      event.preventDefault();

      const button = event.currentTarget;
      button.classList.toggle("favourite");
      button.textContent =
        button.classList.contains("favourite") ? "♥" : "♡";
    });

    card.querySelector(".details-btn").addEventListener("click", () => {
      window.location.href = detailsUrl;
    });

    card.querySelector(".book-btn").addEventListener("click", () => {
      if (!isLoggedIn) {
        window.location.href = "/login";
        return;
      }

      openBooking(p);
    });

    grid.appendChild(card);
  });
}


// Category filter buttons.
document.querySelectorAll(".nav-category").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-category")
      .forEach(item => item.classList.remove("active"));

    button.classList.add("active");
    activeCategory = button.dataset.category;
    loadProperties();
  });
});


// Search form.
searchForm.addEventListener("submit", event => {
  event.preventDefault();
  loadProperties();
});


// Homepage scroll buttons.
document.getElementById("scrollLeft").addEventListener("click", () => {
  grid.scrollBy({ left: -350, behavior: "smooth" });
});

document.getElementById("scrollRight").addEventListener("click", () => {
  grid.scrollBy({ left: 350, behavior: "smooth" });
});


// Booking modal.
const modal = document.getElementById("bookingModal");

function openBooking(property) {
  document.getElementById("bookingPropertyId").value =
    property.Property_ID;

  document.getElementById("modalImage").style.backgroundImage =
    `url("${property.Image_URL || ""}")`;

  document.getElementById("modalTitle").textContent =
    `Reserve ${property.Property_Name}`;

  document.getElementById("modalDescription").textContent =
    `${property.Location} · ${money(property.Price)} per night · ` +
    `★ ${property.Rating}. ${property.Description || ""}`;

  document.getElementById("bookingMessage").textContent = "";
  document.getElementById("bookingMessage").classList.remove("error");

  // Pre-fill the customer's name if available.
  const nameField = document.getElementById("customerName");
  if (nameField && window.APP_USER_NAME) {
    nameField.value = window.APP_USER_NAME;
  }

  modal.classList.remove("hidden");
}


document.getElementById("closeModal").addEventListener("click", () => {
  modal.classList.add("hidden");
});

modal.addEventListener("click", event => {
  if (event.target === modal) {
    modal.classList.add("hidden");
  }
});

document.addEventListener("keydown", event => {
  if (event.key === "Escape") {
    modal.classList.add("hidden");
  }
});


// Send the booking request to Flask.
document.getElementById("bookingForm").addEventListener(
  "submit",
  async event => {
    event.preventDefault();

    if (!isLoggedIn) {
      window.location.href = "/login";
      return;
    }

    const message = document.getElementById("bookingMessage");

    const payload = {
      property_id: document.getElementById("bookingPropertyId").value,
      check_in: document.getElementById("bookingCheckIn").value,
      check_out: document.getElementById("bookingCheckOut").value,
      guests: document.getElementById("bookingGuests").value
    };

    if (!payload.check_in || !payload.check_out) {
      message.textContent = "Please choose both check-in and check-out dates.";
      message.classList.add("error");
      return;
    }

    if (payload.check_out <= payload.check_in) {
      message.textContent = "Check-out must be after check-in.";
      message.classList.add("error");
      return;
    }

    try {
      const response = await fetch("/api/bookings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      message.textContent = result.message;

      message.classList.toggle("error", !response.ok);

      if (response.ok) {
        event.target.reset();
      }
    } catch (error) {
      message.textContent =
        "Could not submit the request. Please check the server.";
      message.classList.add("error");
    }
  }
);


// DSA demonstration.
document.getElementById("runDsa").addEventListener(
  "click",
  async () => {
    const results = document.getElementById("dsaResults");
    results.innerHTML = "<p>Running algorithms…</p>";

    const budget =
      document.getElementById("budgetInput").value || 3000;

    const location =
      document.getElementById("startLocation").value;

    try {
      const response = await fetch(
        `/api/dsa?budget=${encodeURIComponent(budget)}` +
        `&location=${encodeURIComponent(location)}`
      );

      if (!response.ok) {
        throw new Error("DSA request failed");
      }

      const data = await response.json();

      const preorder = data.bst_preorder
        .map(item => `${item.name} (${money(item.price)})`)
        .join(" → ");

      const greedy = data.greedy
        ? `${data.greedy.name} in ${data.greedy.location} — ${money(data.greedy.price)}`
        : "No property fits this budget.";

      results.innerHTML = `
        <div class="result-block">
          <strong>Linked List — Property traversal (${data.linked_list.size} nodes)</strong>
          ${data.linked_list.properties.map(p => `${p.name} (${money(p.price)})`).join(" → ") || "No properties."}
        </div>

        <div class="result-block">
          <strong>Stack — Recently viewed (top first)</strong>
          ${data.recent_stack.map(p => p.name).join(" → ") || "Open a property details page to add it to the stack."}
        </div>

        <div class="result-block">
          <strong>Queue — Booking requests (front first)</strong>
          ${data.booking_queue.map(b => `#${b.booking_id}: ${b.property_name} — ${b.customer_name}`).join(" → ") || "No booking requests in the current session."}
        </div>

        <div class="result-block">
          <strong>Linear Search</strong>
          Used by the destination/property search above.
        </div>

        <div class="result-block">
          <strong>Bubble Sort — Lowest to highest price</strong>
          ${data.sorted_properties.map(p => `${p.name} (${money(p.price)})`).join(" → ") || "No properties found."}
        </div>

        <div class="result-block">
          <strong>BST — Preorder traversal</strong>
          ${preorder || "No properties found."}
        </div>

        <div class="result-block">
          <strong>Graph — BFS from ${location}</strong>
          ${data.bfs.join(" → ") || "No connected locations found."}
        </div>

        <div class="result-block">
          <strong>Greedy — cheapest stay within ${money(budget)}</strong>
          ${greedy}
        </div>
      `;
    } catch (error) {
      results.innerHTML =
        "<p>Could not run the demo. Check the Flask server.</p>";
    }
  }
);


// Load properties when the homepage opens.
loadProperties();