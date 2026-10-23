
document.addEventListener("DOMContentLoaded", () => {
  // Find the authentication form on the current page
  const authForm = document.querySelector(".auth-form");
  const submitButton = document.querySelector(".auth-submit");
  const passwordInput = document.querySelector("#password");
  const emailInput = document.querySelector("#email");

  if (!authForm) return;

  // Validate the form before submitting
  authForm.addEventListener("submit", (event) => {
    if (!authForm.checkValidity()) {
      event.preventDefault();
      authForm.reportValidity();
      return;
    }

    // Basic email validation
    if (emailInput && !emailInput.validity.valid) {
      event.preventDefault();
      emailInput.focus();
      emailInput.reportValidity();
      return;
    }

    // Check password length when minlength is configured
    if (passwordInput && passwordInput.value.length < 8 &&
        passwordInput.minLength >= 8) {
      event.preventDefault();
      passwordInput.setCustomValidity(
        "Your password must contain at least 8 characters."
      );
      passwordInput.reportValidity();
      passwordInput.addEventListener("input", () => {
        passwordInput.setCustomValidity("");
      }, { once: true });
      return;
    }

    // Provide feedback while the form is being submitted
    // The browser will still submit the form to Flask.
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Please wait...";
      submitButton.style.opacity = "0.75";
      submitButton.style.cursor = "wait";
    }
  });

  // Clear validation messages as the user corrects input
  authForm.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", () => {
      input.setCustomValidity("");
    });
  });

  // Add a show/hide password button
  if (passwordInput) {
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    wrapper.style.width = "100%";

    passwordInput.parentNode.insertBefore(wrapper, passwordInput);
    wrapper.appendChild(passwordInput);

    passwordInput.style.paddingRight = "75px";

    const toggleButton = document.createElement("button");
    toggleButton.type = "button";
    toggleButton.textContent = "Show";
    toggleButton.setAttribute("aria-label", "Show password");
    toggleButton.style.position = "absolute";
    toggleButton.style.right = "12px";
    toggleButton.style.top = "50%";
    toggleButton.style.transform = "translateY(-50%)";
    toggleButton.style.border = "none";
    toggleButton.style.background = "transparent";
    toggleButton.style.color = "#e61e4d";
    toggleButton.style.font = "inherit";
    toggleButton.style.fontSize = "13px";
    toggleButton.style.fontWeight = "700";
    toggleButton.style.cursor = "pointer";

    toggleButton.addEventListener("click", () => {
      const showing = passwordInput.type === "text";

      passwordInput.type = showing ? "password" : "text";
      toggleButton.textContent = showing ? "Show" : "Hide";
      toggleButton.setAttribute(
        "aria-label",
        showing ? "Show password" : "Hide password"
      );
    });

    wrapper.appendChild(toggleButton);
  }
});
