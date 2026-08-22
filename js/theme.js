(() => {
  const storageKey = "steele-theme";
  const preferences = ["light", "dark", "auto"];
  const root = document.documentElement;
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");

  const currentPreference = () => {
    const preference = root.dataset.themePreference;
    return preferences.includes(preference) ? preference : "auto";
  };

  const resolveTheme = (preference) => (
    preference === "auto"
      ? (systemTheme.matches ? "dark" : "light")
      : preference
  );

  const siblingAssetUrl = (element, filename) => {
    const currentUrl = element.getAttribute("href") || element.getAttribute("src");
    return new URL(filename, currentUrl ? new URL(currentUrl, document.baseURI) : document.baseURI).href;
  };

  const switchThemeAssets = (resolvedTheme) => {
    const iconFilename = resolvedTheme === "dark"
      ? "icon-on-dark.png"
      : "icon-on-light.png";

    document.querySelectorAll(".navbar-logo, .navbar-brand-logo img").forEach((logo) => {
      const nextUrl = siblingAssetUrl(logo, iconFilename);
      if (logo.src !== nextUrl) logo.src = nextUrl;
    });

    document.querySelectorAll('link[rel~="icon"]').forEach((favicon) => {
      const nextUrl = siblingAssetUrl(favicon, iconFilename);
      if (favicon.href !== nextUrl) favicon.href = nextUrl;
    });
  };

  const updateControl = (preference, resolvedTheme) => {
    document.querySelectorAll("[data-theme-choice]").forEach((button) => {
      const isSelected = button.dataset.themeChoice === preference;
      button.setAttribute("aria-pressed", String(isSelected));

      if (button.dataset.themeChoice === "auto") {
        button.setAttribute("aria-label", `Use browser theme (currently ${resolvedTheme})`);
      }
    });
  };

  const applyTheme = (preference, persist = false) => {
    const resolvedTheme = resolveTheme(preference);
    root.dataset.theme = resolvedTheme;
    root.dataset.themePreference = preference;
    root.style.colorScheme = resolvedTheme;

    if (persist) {
      try {
        window.localStorage.setItem(storageKey, preference);
      } catch (_) {
        // The theme still works for this page when storage is unavailable.
      }
    }

    switchThemeAssets(resolvedTheme);
    updateControl(preference, resolvedTheme);
  };

  const createThemeControl = () => {
    if (document.querySelector("[data-theme-control]")) return;

    const navigation = document.querySelector(".navbar .navbar-nav");
    if (!navigation) return;

    const item = document.createElement("li");
    item.className = "nav-item theme-control-item";

    const control = document.createElement("div");
    control.className = "theme-control";
    control.dataset.themeControl = "";
    control.setAttribute("role", "group");
    control.setAttribute("aria-label", "Colour theme");

    preferences.forEach((preference) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.themeChoice = preference;
      button.textContent = preference[0].toUpperCase() + preference.slice(1);
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyTheme(preference, true));
      control.appendChild(button);
    });

    item.appendChild(control);
    navigation.appendChild(item);
  };

  const initialiseTheme = () => {
    createThemeControl();
    applyTheme(currentPreference());
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiseTheme, { once: true });
  } else {
    initialiseTheme();
  }

  const handleSystemThemeChange = () => {
    if (currentPreference() === "auto") applyTheme("auto");
  };

  if (typeof systemTheme.addEventListener === "function") {
    systemTheme.addEventListener("change", handleSystemThemeChange);
  } else {
    systemTheme.addListener(handleSystemThemeChange);
  }
})();
