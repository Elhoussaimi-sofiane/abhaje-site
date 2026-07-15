const shellHeader = document.getElementById('site-shell-header');
const shellFooter = document.getElementById('site-shell-footer');

if (shellHeader) {
  shellHeader.innerHTML = `
    <header class="site-header" id="accueil">
      <div class="container nav-wrap">
        <a class="brand" href="index.html" aria-label="ABHAJE & Frères — Accueil">
          <img src="assets/images/logo.png" alt="ABHAJE & Frères">
          <span><strong>ABHAJE</strong><small>& Frères</small></span>
        </a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav">
          <span></span><span></span><span></span><span class="sr-only">Ouvrir le menu</span>
        </button>
        <nav class="main-nav" id="main-nav" aria-label="Navigation principale">
          <a href="index.html">Accueil</a>
          <div class="nav-dropdown" data-nav-group="projects">
            <button class="nav-dropdown-toggle" type="button" aria-expanded="false">Nos Projets <span class="dropdown-indicator" aria-hidden="true"></span></button>
            <div class="nav-submenu"><a href="realisations.html">Nos Réalisations</a><a href="projets-en-cours.html">Nos Projets en cours</a></div>
          </div>
          <div class="nav-dropdown" data-nav-group="activities">
            <button class="nav-dropdown-toggle" type="button" aria-expanded="false">Activités Domaine <span class="dropdown-indicator" aria-hidden="true"></span></button>
            <div class="nav-submenu"><a href="routiers.html">Routiers</a><a href="batiments.html">Bâtiments</a></div>
          </div>
          <a href="index.html#profil">Profil</a>
          <div class="nav-dropdown" data-nav-group="locations">
            <button class="nav-dropdown-toggle" type="button" aria-expanded="false">Nos lieux <span class="dropdown-indicator" aria-hidden="true"></span></button>
            <div class="nav-submenu nav-submenu-wide"><a href="siege-ouled-berhil.html">Siège social Ouled Berhil Taroudannt</a><a href="succursale-tassila.html">Succursale Zone Industrielle Tassila–Agadir</a><a href="usine-ouled-aissa.html">Usine Ouled Aissa</a></div>
          </div>
          <a class="nav-cta" href="index.html#contact">Contact</a>
        </nav>
      </div>
    </header>`;
}

if (shellFooter) {
  shellFooter.innerHTML = `
    <footer class="subpage-footer">
      <div class="container">
        <span>© ${new Date().getFullYear()} ABHAJE & Frères. Tous droits réservés.</span>
        <a href="index.html#contact">contact@abhaje.ma</a>
      </div>
    </footer>`;
}
