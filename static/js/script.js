function showRegister() {
  // modal login
  const authModal = document.getElementById("authModal");

  // modal register
  const registerModal = document.getElementById("registerModal");

  // ambil instance login
  const login = bootstrap.Modal.getOrCreateInstance(authModal);

  // tutup login
  login.hide();

  // buka register
  const register = bootstrap.Modal.getOrCreateInstance(registerModal);

  register.show();
}
function showLogin() {
  let registerModal = bootstrap.Modal.getInstance(document.getElementById("registerModal"));

  registerModal.hide();

  let loginModal = new bootstrap.Modal(document.getElementById("authModal"));

  loginModal.show();
}
const tesCards = document.querySelectorAll(".tes-option");

tesCards.forEach((card) => {
  card.addEventListener("click", () => {
    tesCards.forEach((item) => {
      item.classList.remove("active");
    });

    card.classList.add("active");
  });
});
const consentCheck = document.getElementById("consentCheck");

const btnSetuju = document.getElementById("btnSetuju");

if (consentCheck && btnSetuju) {
  consentCheck.addEventListener("change", function () {
    if (consentCheck.checked) {
      btnSetuju.classList.remove("disabled");
    } else {
      btnSetuju.classList.add("disabled");
    }
  });
}
const form = document.getElementById("tesForm");

const warningText = document.getElementById("warningText");

if (form && warningText) {
  form.addEventListener("submit", function (e) {
    const semuaRadio = document.querySelectorAll('input[type="radio"]');

    const semuaName = [];

    semuaRadio.forEach((radio) => {
      if (!semuaName.includes(radio.name)) {
        semuaName.push(radio.name);
      }
    });

    let semuaTerjawab = true;

    semuaName.forEach((name) => {
      const checked = document.querySelector(`input[name="${name}"]:checked`);

      if (!checked) {
        semuaTerjawab = false;
      }
    });

    if (!semuaTerjawab) {
      e.preventDefault();

      warningText.style.display = "block";
    } else {
      warningText.style.display = "none";
    }
  });
}
window.addEventListener("scroll", function () {
  const navbar = document.querySelector(".navbar");

  if (window.scrollY > 50) {
    navbar.classList.add("navbar-scrolled");
  } else {
    navbar.classList.remove("navbar-scrolled");
  }
});
function showLogoutModal() {
  document.getElementById("logoutModal").style.display = "flex";
}

function closeLogoutModal() {
  document.getElementById("logoutModal").style.display = "none";
}
console.log("JS BERHASIL DIMUAT");
document.addEventListener("DOMContentLoaded", () => {

    const searchInput = document.getElementById("searchUser");

    if (!searchInput) return;

    searchInput.addEventListener("input", () => {

        const keyword = searchInput.value
            .trim()
            .toLowerCase();

        const rows = document.querySelectorAll("#userTable tr");

        rows.forEach((row, index) => {

            // Header tabel
            if (index === 0) return;

            const nama = row.cells[0]?.textContent
                .trim()
                .toLowerCase();

            row.style.display =
                nama.includes(keyword)
                ? ""
                : "none";
        });

    });

});
