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
          <a href="index.html">Acceuil</a>
          <a href="profil.html">Profil</a>
          <div class="nav-dropdown" data-nav-group="projects">
            <button class="nav-dropdown-toggle" type="button" aria-expanded="false">Nos Projets <span class="dropdown-indicator" aria-hidden="true"></span></button>
            <div class="nav-submenu nav-mega-menu">
              <div class="nav-menu-column">
                <a class="nav-menu-heading" href="nos-projets.html">Nos Projets</a>
                <a href="realisations.html">Nos Realisations</a>
                <a href="projets-en-cours.html">Nos Projets en cours</a>
              </div>
              <div class="nav-menu-column">
                <span class="nav-menu-heading">Dernier Nos Projets</span>
                <a href="faculte-agadir.html">La facultés de Médecine à Agadir</a>
                <a href="tribunal-agadir.html">Tribunal de Premiere Instance D'Agadir</a>
                <a href="province-de-fqih-ben-salh.html">Province de Fqih Ben Salh</a>
                <a href="province-de-sidi-bennour.html">Province de Sidi Bennour</a>
              </div>
            </div>
          </div>
          <div class="nav-dropdown" data-nav-group="activities">
            <button class="nav-dropdown-toggle" type="button" aria-expanded="false">Activites Domaine <span class="dropdown-indicator" aria-hidden="true"></span></button>
            <div class="nav-submenu nav-mega-menu nav-mega-menu-activities">
              <div class="nav-menu-column">
                <a class="nav-menu-heading" href="routiers.html">Routiers</a>
                <a href="terrasement.html">Trassements</a>
                <a href="travaux-routiere.html">Travaux Routiere</a>
                <a href="ouvrage-d-art-routier.html">Ouvrage d'art routier</a>
                <a href="enrobes-routiers.html">Enrobés routiers</a>
              </div>
              <div class="nav-menu-column">
                <a class="nav-menu-heading" href="batiments.html">Batiments</a>
                <a href="gros-oeuvres.html">Gros oeuvres</a>
                <a href="etancheite.html">Etanchéité</a>
                <a href="lot-techniques.html">Lot Techniques</a>
                <a href="lot-secondaires.html">Lot Secondaires</a>
              </div>
              <div class="nav-menu-column">
                <span class="nav-menu-heading">Lots spécialisés</span>
                <a href="electricite-et-lustrerie.html">Electricite et Lustrerie</a>
                <a href="ventilation-et-climatisation.html">Ventilation et Climatisation</a>
                <a href="plomberie-et-sanitaire.html">Plomberie et Sanitaire</a>
                <a href="revetement-de-sol-et-mur.html">Revêtement de Sol et Mur</a>
                <a href="peinture.html">Peinture</a>
                <a href="menuiserie-en-bois-et-aluminium.html">Menuiserie en Bois et Aluminium</a>
                <a href="menuiserie-en-metallique.html">Menuiserie en Metallique</a>
                <a href="amenagement-exterieurs-et-epsaces-vert.html">AMENAGEMENT EXTERIEURS ET EPSACES VERT</a>
              </div>
            </div>
          </div>
          <div class="nav-dropdown" data-nav-group="locations">
            <button class="nav-dropdown-toggle" type="button" aria-expanded="false">Nos lieux <span class="dropdown-indicator" aria-hidden="true"></span></button>
            <div class="nav-submenu nav-submenu-wide"><a href="nos-lieux.html">Nos lieux</a><a href="siege-ouled-berhil.html">Siege social Ouled Berhil Taroudannt</a><a href="succursale-tassila.html">Succursale Zone Industiel Tassila-Agadir</a><a href="usine-ouled-aissa.html">Usine Ouled Aissa</a></div>
          </div>
          <a class="nav-cta" href="contact.html">Contact</a>
        </nav>
      </div>
    </header>`;
}

if (shellFooter) {
  shellFooter.innerHTML = `
    <footer class="site-footer">
      <div class="container footer-grid">
        <div class="footer-brand">
          <a class="brand brand-light" href="index.html" aria-label="ABHAJE & Frères — Accueil">
            <img src="assets/images/logo.png" alt="ABHAJE & Frères">
            <span><strong>ABHAJE</strong><small>& Frères</small></span>
          </a>
          <p>Construire avec exigence, livrer avec confiance.</p>
        </div>
        <div>
          <h3>Navigation</h3>
          <a href="activites-domaine.html">Nos Activités</a>
          <a href="realisations.html">Nos Réalisations</a>
          <a href="nos-projets.html">Nos Projets</a>
        </div>
        <div>
          <h3>Entreprise</h3>
          <a href="profil.html">Nos Profiles</a>
          <a href="nos-lieux.html">Nos lieux</a>
          <a href="contact.html">Contact</a>
        </div>
        <div>
          <h3>Contact</h3>
          <p>Agadir, Maroc</p>
          <a href="tel:+212528531453">+212 528 531 453</a>
          <a href="mailto:contact@abhaje.ma">contact@abhaje.ma</a>
        </div>
      </div>
      <div class="container footer-bottom">
        <span>© ${new Date().getFullYear()} ABHAJE & Frères. Tous droits réservés.</span>
        <a href="#accueil">Retour en haut</a>
      </div>
    </footer>`;
}
