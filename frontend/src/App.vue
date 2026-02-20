<template>
  <div class="layout">
    <nav :class="['sidebar', { reduit: menuReduit }]">
      <button class="btn-toggle-menu hide-on-mobile" @click="menuReduit = !menuReduit">{{ menuReduit ? '›' : '‹' }}</button>
      <button class="btn-close-mobile show-on-mobile" @click="menuMobileOuvert = false">×</button>

      <div class="logo-container" :class="{ 'logo-reduit': menuReduit }">
        <img :src="logoImg" alt="My Secret Garden Logo" class="logo-img" />
        <h1 v-if="!menuReduit" class="titre-sensuel">My Secret Garden</h1>
      </div>
      
      <ul>
        <li :class="{ actif: vueActive === 'potager' }" @click="changerVue('potager')" title="Mon Potager">
          <span class="icone">◩</span> <span class="texte-menu" v-if="!menuReduit">Plan du Potager</span>
        </li>
        <li :class="{ actif: vueActive === 'grainotheque' }" @click="changerVue('grainotheque')" title="La Grainothèque">
          <span class="icone">❦</span> <span class="texte-menu" v-if="!menuReduit">La Grainothèque</span>
        </li>
        <li :class="{ actif: vueActive === 'godets' }" @click="changerVue('godets')" title="Mes Godets">
          <span class="icone">🪴</span> <span class="texte-menu" v-if="!menuReduit">Mes Godets</span>
        </li>
        <li :class="{ actif: vueActive === 'conseils' }" @click="changerVue('conseils')" title="Associations">
          <span class="icone">🤝</span> <span class="texte-menu" v-if="!menuReduit">Associations</span>
        </li>
        <li :class="{ actif: vueActive === 'rotation' }" @click="changerVue('rotation')" title="Rotation des cultures">
          <span class="icone">🔄</span> <span class="texte-menu" v-if="!menuReduit">Rotation</span>
        </li>
        <li :class="{ actif: vueActive === 'notifications' }" @click="changerVue('notifications')" title="Notifications">
          <span class="icone">🔔</span> <span class="texte-menu" v-if="!menuReduit">Notifications</span>
          <span v-if="totalAlertes > 0 && !menuReduit" class="badge-notif">{{ totalAlertes }}</span>
          <span v-if="totalAlertes > 0 && menuReduit" class="badge-notif-mini"></span>
        </li>
        <li :class="{ actif: vueActive === 'recapitulatif' }" @click="changerVue('recapitulatif')" title="Récapitulatif">
          <span class="icone">⊞</span> <span class="texte-menu" v-if="!menuReduit">Vue d'ensemble</span>
        </li>
        <li :class="{ actif: vueActive === 'reglages' }" @click="changerVue('reglages')" title="Réglages">
          <span class="icone">⚙</span> <span class="texte-menu" v-if="!menuReduit">Réglages</span>
        </li>
      </ul>
      
      <div class="menu-bottom-actions">
        <button v-if="alertesArrosage && alertesArrosage.length > 0" class="btn-arroser-tout" @click="declencherArrosageGlobal()" title="Arroser tous les bacs assoiffés">
          <span class="icone">💦</span> <span v-if="!menuReduit">Tout arroser ({{ alertesArrosage.length }})</span>
        </button>

        <button class="btn-ajouter-graine" @click="ouvrirModalGraine()" title="Ajouter une graine">
          <span class="icone">+</span> <span v-if="!menuReduit">Nouvelle semence</span>
        </button>
      </div>
    </nav>
    
    <button class="btn-hamburger show-on-mobile" @click="menuMobileOuvert = true">☰</button>
    <div v-if="menuMobileOuvert" class="mobile-overlay" @click="menuMobileOuvert = false"></div>

    <main class="content">
      
      <div v-if="vueActive === 'potager'" class="vue-potager">
        <div :class="['workspace-terrain', `mode-${saisonActive}`]" @mousedown="commencerAction" @mousemove="actionEnCours" @mouseup="terminerAction" @mouseleave="terminerAction" @touchstart.passive="commencerAction" @touchmove.passive="actionEnCours" @touchend="terminerAction" @wheel.prevent="gererZoom">
          
          <div v-if="pluieGlobaleActive" class="pluie-globale-overlay"></div>
          <div v-if="saisonActive === 'hiver'" class="neige-globale-overlay"></div>

          <div class="hud-left toolbar-vertical">
            <button :class="['btn-tool-v', { actif: outilActif === 'main' }]" @click="outilActif = 'main'" title="Naviguer (Glisser la carte)">⚲</button>
            <div class="separateur-v"></div>
            <button :class="['btn-tool-v', { actif: outilActif === 'bac' }]" @click="outilActif = 'bac'" title="Tracer un bac de culture">⬚</button>
            <button :class="['btn-tool-v', { actif: outilActif === 'bordure' }]" @click="outilActif = 'bordure'" title="Tracer une bordure en bois (Diagonales possibles)">➖</button>
            <button :class="['btn-tool-v', { actif: outilActif === 'arbre' }]" @click="outilActif = 'arbre'" title="Placer un arbre (Clic simple sur la carte)">🌳</button>
            <button :class="['btn-tool-v', { actif: outilActif === 'deco' }]" @click="outilActif = 'deco'" title="Placer une décoration (Clic simple sur la carte)">🦆</button>
            <div class="separateur-v"></div>
            
            <button class="btn-tool-v arrosoir-global-btn" @click="declencherArrosageGlobal" title="Arroser tout le potager">🚿</button>
            <div class="separateur-v hide-on-mobile-small"></div>

            <button class="btn-tool-v hide-on-mobile-small" @click="zoomer(0.1)" title="Zoomer">➕</button>
            <span class="zoom-text-v hide-on-mobile-small">{{ Math.round(zoom * 100) }}%</span>
            <button class="btn-tool-v hide-on-mobile-small" @click="zoomer(-0.1)" title="Dézoomer">➖</button>
            <button class="btn-tool-v hide-on-mobile-small" @click="recentrerTerrain" title="Retourner au centre">⌖</button>
            <div class="separateur-v"></div>

            <button :class="['btn-tool-v', 'btn-saison-v', saisonActive]" @click="basculerSaison" title="Bascule Été/Hiver">
              {{ saisonActive === 'ete' ? '☀️' : '❄️' }}
            </button>
          </div>

          <div ref="terrainRef" class="terrain-infini" :style="{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }">
            <div class="centre-absolu">+ Point Zéro</div>
            
            <div v-for="p in parcelles" :key="p.id" 
                 :class="['element-terrain', `type-${p.type || 'bac'}`, `taille-${p.taille || 'Moyen'}`, { 'en-mouvement': draggedParcelle && draggedParcelle.id === p.id, 'conflit-actif': aConflit(p) }]" 
                 :style="styleTerrainElement(p)" 
                 @mousedown.stop="commencerDragParcelle($event, p)" @touchstart.stop="commencerDragParcelle($event, p)">
              
              <template v-if="!p.type || p.type === 'bac'">
                <div v-if="p.arrosageEnCours" class="pluie-container"></div>
                <div class="terre-interieure">
                  <div class="grille-plantes" :style="calculerGrillePlantes(p)">
                    <div v-for="(plante, index) in obtenirPlantesUnitaires(p)" :key="index" class="plante-visuelle" :title="plante.nom">{{ plante.icone }}</div>
                  </div>
                </div>
                <span class="label-dim"><strong v-if="p.nom">{{ p.nom }} • </strong>{{ p.dimX }} x {{ p.dimY }} cm</span>
                <div v-if="aConflit(p)" class="indicateur-conflit" title="Association défavorable dans ce bac !">⚠️</div>
                <div v-if="bacBesoinEau(p) && !p.arrosageEnCours" class="indicateur-soif" title="Besoin d'eau !">💧</div>
                
                <div class="resize-handle" @mousedown.stop="commencerResize($event, p)" @touchstart.stop="commencerResize($event, p)"></div>
              </template>

              <template v-else-if="p.type === 'deco'">
                <span class="icone-deco">{{ p.icone }}</span>
              </template>
              
              <template v-else-if="p.type === 'bordure'">
                <div class="resize-handle" @mousedown.stop="commencerResize($event, p)" @touchstart.stop="commencerResize($event, p)"></div>
              </template>

              <div class="parcelle-actions-container" :style="styleTooltip(p)">
                <button v-if="!p.type || p.type === 'bac' || p.type === 'arbre'" class="btn-action-parcelle btn-arroser" @click.stop="arroserBac(p)" title="J'ai arrosé !">💦</button>
                <button v-if="!p.type || p.type === 'bac'" class="btn-action-parcelle btn-planter" @click.stop="ouvrirModalPlantation(p)" title="Planter ici">🌱</button>
                <button v-if="!p.type || p.type === 'bac'" class="btn-action-parcelle btn-gerer" @click.stop="ouvrirModalGestionBac(p)" title="Gérer ce bac">📋</button>
                <button v-if="!p.type || p.type === 'bac'" class="btn-action-parcelle btn-historique" @click.stop="ouvrirHistorique(p)" title="Voir l'historique">🕒</button>
                <button class="btn-action-parcelle btn-supprimer" @click.stop="supprimerParcelle(p.id)" title="Supprimer">×</button>
              </div>
            </div>
            
            <div v-if="parcelleEnCours" :class="['element-terrain', 'en-cours-dessin', `type-${parcelleEnCours.type}`]" :style="styleTerrainElement(parcelleEnCours)">
              <div v-if="!parcelleEnCours.type || parcelleEnCours.type === 'bac'" class="terre-interieure"></div>
              <span class="label-dim" v-if="!parcelleEnCours.type || parcelleEnCours.type === 'bac'">{{ parcelleEnCours.dimX }} x {{ parcelleEnCours.dimY }} cm</span>
            </div>
          </div>
        </div>

        <aside :class="['panel-historique', { 'ouvert': parcelleHistoriqueSelectionnee }]">
          <div class="ph-header">
            <h3>Chronologie du bac</h3>
            <button class="btn-fermer-ph" @click="fermerHistorique">×</button>
          </div>
          <div class="ph-content">
            <div v-if="historiqueParcelle.length === 0" class="etat-vide-petit">Aucune plantation enregistrée.</div>
            <div class="timeline" v-else>
              <div v-for="groupe in historiqueParcelle" :key="groupe.date" class="tl-item">
                <div class="tl-date">{{ groupe.formatted }}</div>
                <div class="tl-plantes">
                  <div v-for="(pl, i) in groupe.plantes" :key="i" class="tl-plante">
                    <span class="tl-icone" :style="pl.active ? '' : 'opacity:0.5; filter:grayscale(1);'">{{ pl.icone }}</span>
                    <div class="tl-info">
                      <span :class="['tl-nom', { 'plante-archivee': !pl.active }]">{{ pl.nom }} <b>(x{{ pl.quantite }})</b></span>
                      <div style="display:flex; gap: 6px; margin-top: 4px;">
                        <span :class="['badge-saison-petit', pl.saison]">{{ pl.saison === 'ete' ? '☀️ Été' : '❄️ Hiver' }}</span>
                        <span v-if="!pl.active" class="badge-saison-petit archive" :title="'Récolté/Retiré le ' + pl.date_retrait">Récolté</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <div v-if="vueActive === 'grainotheque'" class="vue-grainotheque vue-scrollable">
        <header class="header-epure flex-between block-mobile">
          <div>
            <h2>Inventaire des semences</h2>
            <p class="sous-titre">Gérez vos variétés, leurs cycles et leurs besoins en sol.</p>
            <div class="legende-possession mt-15">
              <span class="info-bulle">💡 <b>Astuce :</b> Vous pouvez ajouter n'importe quelle graine à l'encyclopédie. Cliquez sur le bouton <b>"🛒 À acheter"</b> ou <b>"📦 En stock"</b> d'une carte pour indiquer si vous la possédez physiquement.</span>
            </div>
          </div>
          <button class="btn-submit full-width mt-mobile" style="align-self: flex-start;" @click="ouvrirModalGraine()">+ Nouvelle semence</button>
        </header>
        
        <div class="workspace-graines">
          <div class="filtres-bar block-mobile">
            <div class="form-group search-group full-width">
              <span class="search-icon">🔍</span>
              <input type="text" v-model="rechercheGraine" placeholder="Rechercher une variété..." />
            </div>
            <div class="form-group select-group full-width">
              <select v-model="filtreTypeGraine">
                <option value="">Tous les types botaniques</option>
                <option v-for="t in typesPlantes" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div class="form-group toggle-group full-width mt-mobile" style="display: flex; align-items: center; padding-left: 10px;">
              <label class="toggle-container">
                <input type="checkbox" v-model="filtrePossession">
                <span class="toggle-slider"></span>
                <span class="toggle-label">En stock uniquement</span>
              </label>
            </div>
          </div>

          <div class="grid-graines">
            <div v-for="graine in grainesFiltrees" :key="graine.id" class="carte-graine">
              <div class="carte-actions">
                <button class="btn-icon" @click="ouvrirModalGraine(graine)" title="Modifier">✎</button>
                <button class="btn-icon rouge" @click="supprimerGraine(graine.id)" title="Supprimer">×</button>
              </div>
              <div class="carte-contenu">
                <div class="carte-top">
                  <div class="icone-graine">{{ graine.icone }}</div>
                  <div class="titre-graine">
                    <div class="titre-avec-badge block-mobile-small">
                      <h3>{{ graine.nom }}</h3>
                      <div style="display:flex; gap:8px;">
                        <button :class="['badge-action-possession', { 'possede': graine.en_possession }]" @click.stop="graine.en_possession = !graine.en_possession">
                          {{ graine.en_possession ? '📦 En stock' : '🛒 À acheter' }}
                        </button>
                        <span v-if="estEnGodet(graine.id)" class="badge-godet-actif">🪴 En godet</span>
                      </div>
                    </div>
                    <span class="badge">{{ graine.type }}</span>
                  </div>
                </div>
                <div class="infos-agronomiques">
                  <div class="infos-agronomiques-mini-grid">
                    <p v-if="graine.sol" class="info-tag"><strong>Sol:</strong> {{ graine.sol }}</p>
                    <p v-if="graine.arrosage" class="info-tag"><strong>Eau:</strong> {{ getArrosageLabel(graine.arrosage) }}</p>
                  </div>
                  <div class="ligne-saison" v-if="graine.godet_debut && graine.godet_fin"><span class="saison-icone">🪴</span><span class="saison-texte">Mise en godet : {{ graine.godet_debut.substring(0,3) }}. à {{ graine.godet_fin.substring(0,3) }}.</span></div>
                  <div class="ligne-saison" v-if="graine.plantation_debut && graine.plantation_fin"><span class="saison-icone">🌱</span><span class="saison-texte">Pleine terre : {{ graine.plantation_debut.substring(0,3) }}. à {{ graine.plantation_fin.substring(0,3) }}.</span></div>
                  <div class="ligne-saison" v-if="graine.recolte_debut && graine.recolte_fin"><span class="saison-icone">🧺</span><span class="saison-texte">Récolte : {{ graine.recolte_debut.substring(0,3) }}. à {{ graine.recolte_fin.substring(0,3) }}.</span></div>
                </div>
              </div>
            </div>
            
            <div v-if="grainesFiltrees.length === 0" class="etat-vide pleine-largeur">
              <div class="etat-vide-icone">🔍</div>
              <h3>Aucune semence ne correspond à votre recherche.</h3>
            </div>
          </div>
        </div>
      </div>

      <div v-if="vueActive === 'godets'" class="vue-godets vue-scrollable">
        <header class="header-epure flex-between block-mobile">
          <div>
            <h2>Mes semis en godets</h2>
            <p class="sous-titre">Suivez la croissance de vos semis avant le repiquage.</p>
          </div>
          <button class="btn-submit full-width mt-mobile" @click="ouvrirModalAjoutGodet()">+ Nouveau godet</button>
        </header>

        <div class="workspace-graines">
          <div v-if="!godetsAffichables || godetsAffichables.length === 0" class="etat-vide">
            <div class="etat-vide-icone">🪴</div>
            <h3>Votre pouponnière est vide</h3>
          </div>
          <div class="grid-graines" v-else>
            <div v-for="godet in godetsAffichables" :key="godet.id" class="carte-graine carte-godet">
              <div class="carte-actions">
                <button class="btn-icon" @click="ouvrirModalAjoutGodet(godet)" title="Modifier">✎</button>
                <button class="btn-icon rouge" @click="supprimerGodet(godet.id)" title="Supprimer">✔</button>
              </div>
              <div class="carte-contenu">
                <div class="carte-top align-center">
                  <div class="icone-graine">{{ godet.icone }}</div>
                  <div class="titre-graine flex-grow">
                    <h3>{{ godet.nom }}</h3>
                    <span class="badge">{{ godet.type }}</span>
                  </div>
                  <div class="bulle-quantite godet-bulle">
                    <span class="qte-nombre">{{ godet.quantite }}</span>
                    <span class="qte-label">Pots</span>
                  </div>
                </div>
                <div class="infos-agronomiques mt-15" v-if="godet.emplacement">
                  <div class="ligne-saison">
                    <span class="saison-icone">📍</span>
                    <span class="saison-texte"><strong>Emplacement :</strong> {{ godet.emplacement }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="vueActive === 'conseils'" class="vue-conseils vue-scrollable">
        <header class="header-epure">
          <h2>Compagnonnage Végétal</h2>
          <p class="sous-titre">Découvrez quelles plantes associer pour stimuler la croissance.</p>
        </header>
        
        <div class="workspace-graines">
          <div class="filtres-bar">
            <div class="form-group search-group full-width">
              <span class="search-icon">🔍</span>
              <input type="text" v-model="rechercheConseil" placeholder="Rechercher un légume (ex: Tomate, Ail...)" />
            </div>
          </div>

          <div class="grid-graines">
            <div v-for="(assoc, index) in conseilsFiltres" :key="index" class="carte-graine carte-conseil">
              <div class="carte-contenu">
                <h3 class="assoc-titre">{{ assoc.plante }}</h3>
                <div class="assoc-bloc fav">
                  <div class="assoc-header"><span class="assoc-icon">✨</span><strong>Associations Favorables</strong></div>
                  <div class="tags-container">
                    <span v-for="p in assoc.fav" :key="'f'+p" class="tag tag-fav">{{ p }}</span>
                  </div>
                </div>
                <div class="assoc-bloc defav mt-15">
                  <div class="assoc-header"><span class="assoc-icon">⚠️</span><strong>Associations Défavorables</strong></div>
                  <div class="tags-container">
                    <span v-for="p in assoc.defav" :key="'d'+p" class="tag tag-defav">{{ p }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="conseilsFiltres.length === 0" class="etat-vide pleine-largeur">
              <div class="etat-vide-icone">🌱</div><h3>Aucune plante trouvée dans l'encyclopédie.</h3>
            </div>
          </div>
        </div>
      </div>

      <div v-if="vueActive === 'rotation'" class="vue-rotation vue-scrollable">
        <header class="header-epure">
          <h2>Rotation des Cultures</h2>
          <p class="sous-titre">Le principe de base pour préserver votre sol : ne plantez jamais la même famille de légumes au même endroit d'une année sur l'autre.</p>
        </header>

        <div class="info-bulle mb-30" style="display:block;">
          💡 <b>Comment ça marche ?</b> Divisez votre potager en 4 zones (ou 4 bacs). Chaque année, décalez les groupes d'une zone à l'autre. Ce cycle de 4 ans évite l'épuisement du sol, freine la propagation des maladies et réduit l'utilisation d'engrais.
        </div>

        <div class="rotation-grid">
          <div v-for="(cat, index) in rotationCategories" :key="cat.id" class="carte-rotation">
            <div class="rotation-header" :class="cat.id">
              <span class="step-badge">Année {{ index + 1 }}</span>
              <h3>{{ cat.nom }}</h3>
            </div>
            <div class="carte-contenu-rot">
              <p class="desc-rotation">{{ cat.desc }}</p>
              <div class="tags-container mt-15">
                <span v-for="p in cat.plantes" :key="p" class="tag tag-rotation">{{ p }}</span>
              </div>
            </div>
            <div v-if="index < 3" class="arrow-next hide-on-mobile">➔</div>
            <div v-if="index < 3" class="arrow-next show-on-mobile-inline">⬇</div>
          </div>
        </div>

        <div class="mt-30">
          <h3 class="section-titre">Mémento détaillé par végétal</h3>
          <div class="table-responsive">
            <table class="table-familles">
              <thead>
                <tr>
                  <th>Catégorie</th>
                  <th>Plantes / Légumes</th>
                  <th>Mise en terre</th>
                  <th>Saison</th>
                  <th>Exposition</th>
                  <th>Arrosage</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in besoinsFamilles" :key="item.plante">
                  <td><span :class="['badge-famille', item.type]">{{ item.labelType }}</span></td>
                  <td><strong>{{ item.plante }}</strong></td>
                  <td>{{ item.plantation }}</td>
                  <td>{{ item.saison }}</td>
                  <td>{{ item.soleil }}</td>
                  <td>{{ item.arrosage }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="mt-30">
          <h3 class="section-titre">Comment nourrir son sol au fil des saisons ?</h3>
          <div class="tips-grid">
            <div v-for="tip in enrichissementSaisons" :key="tip.saison" class="tip-card">
              <div class="tip-icon">{{ tip.icone }}</div>
              <div class="tip-content">
                <h4>{{ tip.saison }}</h4>
                <p>{{ tip.texte }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div v-if="vueActive === 'notifications'" class="vue-notifications vue-scrollable">
        <header class="header-epure flex-between block-mobile">
          <div>
            <h2>Centre de Notifications</h2>
            <p class="sous-titre">Gérez les alertes de votre potager.</p>
          </div>
          <button v-if="alertesArrosage.length > 0" class="btn-arroser-petit full-width mt-mobile" @click="declencherArrosageGlobal()">💦 Tout arroser</button>
        </header>

        <div v-if="totalAlertes === 0" class="etat-vide">
          <div class="etat-vide-icone">✨</div>
          <h3>Tout est à jour !</h3>
        </div>

        <div class="alertes-grid" v-else>
          <div class="alertes-container arrosage-container" v-if="alertesArrosage.length > 0">
            <h3><span class="icone-h3">💧</span> Bacs nécessitant de l'eau</h3>
            <div class="liste-alertes">
              <div v-for="alerte in alertesArrosage" :key="'arr'+alerte.id" class="alerte-item arrosage block-mobile">
                <div class="alerte-icone hide-on-mobile-small">💦</div>
                <div class="alerte-texte">
                  Le <strong>{{ alerte.nom || 'Bac sans nom' }}</strong> a besoin d'être arrosé ! 
                  <span class="arrosage-sous-texte">Dernier arrosage il y a {{ alerte.joursDepuis }} jour(s).</span>
                </div>
                <button class="btn-arroser-petit full-width" @click="arroserBac(alerte.bac); allerAuBac(alerte.bac);">J'ai arrosé</button>
              </div>
            </div>
          </div>

          <div class="alertes-container" v-if="alertesSaisonsFiltrees.length > 0">
            <h3><span class="icone-h3">📅</span> Tâches du Calendrier (Ce mois & Mois prochain)</h3>
            <div class="liste-alertes">
              <div v-for="(alerte, i) in alertesSaisonsFiltrees" :key="i" :class="['alerte-item', alerte.type]">
                <div class="alerte-icone">{{ alerte.icone }}</div>
                <div class="alerte-texte">
                  <strong>{{ alerte.dist === 0 ? 'Ce mois-ci' : `Dans ${alerte.dist} mois` }}</strong> : 
                  {{ alerte.type === 'godet' ? 'Mettre en godet' : (alerte.type === 'semis' ? 'Planter au potager' : 'Récolter') }} 
                  <b>{{ alerte.plante }}</b> ({{ alerte.mois }})
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="vueActive === 'recapitulatif'" class="vue-recapitulatif vue-scrollable">
        <header class="header-epure">
          <h2>Vue d'ensemble</h2>
          <p class="sous-titre">Météo et bilan du potager de la saison en cours.</p>
        </header>

        <div class="meteo-dashboard mb-30">
          <template v-if="meteoInfo && !meteoErreur">
            <div class="meteo-current">
              <div class="meteo-city">📍 {{ meteoInfo.cityName }}</div>
              <div class="meteo-main">
                <div class="meteo-icon-large">{{ getWeatherEmoji(meteoInfo.current_weather.weathercode) }}</div>
                <div class="meteo-temp-large">{{ Math.round(meteoInfo.current_weather.temperature) }}°C</div>
              </div>
              <div class="meteo-desc">Temps actuel</div>
            </div>
            <div class="meteo-forecast-grid">
              <div v-for="(day, n) in 3" :key="n" class="forecast-card">
                <span class="fc-date">{{ formatJour(meteoInfo.daily.time[n+1]) }}</span>
                <span class="fc-icon">{{ getWeatherEmoji(meteoInfo.daily.weathercode[n+1]) }}</span>
                <span class="fc-temp">{{ Math.round(meteoInfo.daily.temperature_2m_max[n+1]) }}° / {{ Math.round(meteoInfo.daily.temperature_2m_min[n+1]) }}°</span>
              </div>
            </div>
          </template>
          <template v-else-if="meteoErreur">
            <div class="meteo-placeholder erreur" @click="changerVue('reglages')">
              <span class="placeholder-icon">⚠️</span>
              <div class="placeholder-texte"><strong>Ville introuvable</strong><p>Vérifiez l'orthographe.</p></div>
            </div>
          </template>
          <template v-else>
            <div class="meteo-placeholder" @click="changerVue('reglages')">
              <span class="placeholder-icon">🌤️</span>
              <div class="placeholder-texte"><strong>Configurez la météo</strong></div>
            </div>
          </template>
        </div>

        <div class="stats-dashboard mt-30 block-mobile">
          <div class="stat-box full-width"><span class="stat-valeur">{{ totalPlantsCultives }}</span><span class="stat-label">Plants en terre</span></div>
          <div class="stat-box full-width"><span class="stat-valeur">{{ totalGodetsCultives }}</span><span class="stat-label">Plants en godets</span></div>
          <div class="stat-box full-width"><span class="stat-valeur">{{ bacsUtilises }} / {{ bacsTotal }}</span><span class="stat-label">Bacs potagers ({{ saisonActive }})</span></div>
        </div>

        <div class="workspace-graines">
          <div v-if="culturesPlantees.length === 0" class="etat-vide"><div class="etat-vide-icone">🪴</div><h3>Votre potager est vierge pour cette saison.</h3></div>
          <div class="grid-graines" v-else>
            <div v-for="culture in culturesPlantees" :key="culture.id" class="carte-graine carte-recap">
              <div class="carte-contenu">
                <div class="carte-top align-center">
                  <div class="icone-graine-petit">{{ culture.icone }}</div>
                  <div class="titre-graine flex-grow"><h3>{{ culture.nom }}</h3><span class="badge">{{ culture.type }}</span></div>
                  <div class="bulle-quantite"><span class="qte-nombre">{{ culture.quantiteTotale }}</span><span class="qte-label">plants</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="vueActive === 'reglages'" class="vue-reglages vue-scrollable">
        <header class="header-epure"><h2>Configuration du système</h2></header>

        <div class="grid-reglages">
          <div class="carte-reglage carte-discord" style="grid-column: 1 / -1;">
            <div class="reglage-header"><div class="reglage-icone">💬</div><h3>Notifications Discord</h3></div>
            <div class="reglage-body">
              <div class="form-group">
                <label>URL du Webhook Discord</label>
                <div class="input-action flex-col-mobile">
                  <input type="url" v-model="reglages.webhookUrl" placeholder="https://discord.com/api/webhooks/..." />
                  <button class="btn-submit full-width-mobile" @click="testerWebhookDiscord" :disabled="!reglages.webhookUrl">Tester</button>
                </div>
              </div>
              <div class="form-group mt-15" style="max-width: 200px;">
                <label>Heure d'envoi automatique (HH:MM)</label>
                <input type="time" v-model="reglages.webhookHeure" class="full-width-mobile" />
              </div>
              <div class="form-group mt-15">
                <label class="toggle-container">
                  <input type="checkbox" v-model="reglages.webhookArrosage">
                  <span class="toggle-slider"></span>
                  <span class="toggle-label">Alerte : "Jour d'arrosage pour : XXX" 💦</span>
                </label>
              </div>
              <div class="form-group mt-15">
                <label class="toggle-container">
                  <input type="checkbox" v-model="reglages.webhookPluie">
                  <span class="toggle-slider"></span>
                  <span class="toggle-label">Alerte : "Il pleut aujourd'hui..." 🌧️</span>
                </label>
              </div>
            </div>
          </div>

          <div class="carte-reglage carte-localisation">
            <div class="reglage-header"><div class="reglage-icone">🌤️</div><h3>Localisation & Météo</h3></div>
            <div class="reglage-body">
              <div class="form-row block-mobile">
                <div class="form-group flex-grow full-width"><label>Ville (ex: Paris)</label><input type="text" v-model="reglages.ville" placeholder="Nom de la ville" @blur="chargerMeteo" @keyup.enter="chargerMeteo" /></div>
              </div>
              <div v-if="meteoErreur" class="help-text mt-5">❌ Impossible de trouver cette ville.</div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div v-if="afficherModalArbre" class="modal-overlay" @click.self="afficherModalArbre = false">
      <div class="modal">
        <h3>Placer un objet 🏡</h3>
        <form @submit.prevent="validerAjoutArbre">
          <div class="form-group">
            <label>Taille de l'arbre sur la carte</label>
            <select v-model="nouvelArbre.taille" required>
              <option value="Petit">Petit (Arbuste)</option>
              <option value="Moyen">Moyen (Fruitier classique)</option>
              <option value="Grand">Grand (Chêne, Noyer...)</option>
            </select>
          </div>
          <div class="actions block-mobile mt-30">
            <button type="button" class="btn-cancel full-width" @click="afficherModalArbre = false">Annuler</button>
            <button type="submit" class="btn-submit full-width">Placer sur la carte</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="afficherModalDeco" class="modal-overlay" @click.self="afficherModalDeco = false">
      <div class="modal">
        <h3>Placer une décoration ✨</h3>
        <p class="sous-titre mb-15">Choisissez un objet ou un animal pour décorer votre plan.</p>
        
        <div class="grille-emojis-deco">
          <span v-for="emoji in listeDecos" :key="emoji" 
                :class="['emoji-deco-item', { actif: nouvelleDeco.icone === emoji }]" 
                @click="nouvelleDeco.icone = emoji">{{ emoji }}</span>
        </div>

        <div class="actions block-mobile mt-30">
          <button type="button" class="btn-cancel full-width" @click="afficherModalDeco = false">Annuler</button>
          <button class="btn-submit full-width" @click="validerAjoutDeco" :disabled="!nouvelleDeco.icone">Poser ici</button>
        </div>
      </div>
    </div>

    <div v-if="afficherModal" class="modal-overlay" @click.self="afficherModal = false">
      <div class="modal modal-large">
        <h3>{{ modeEdition ? 'Modifier la semence' : 'Ajouter une semence' }}</h3>
        <form @submit.prevent="sauvegarderGraine">
          <div class="form-row block-mobile"><div class="form-group icone-selector-container full-width"><label>Icône</label><div class="icone-selector"><span v-for="ico in listeIcones" :key="ico" :class="['ico-choix', { 'ico-actif': nouvelleGraine.icone === ico }]" @click="nouvelleGraine.icone = ico">{{ ico }}</span></div></div><div class="form-group flex-grow full-width"><label>Nom de la variété *</label><input v-model="nouvelleGraine.nom" required /></div></div>
          
          <div class="form-row block-mobile">
            <div class="form-group third full-width"><label>Catégorie botanique *</label><select v-model="nouvelleGraine.type" required><option v-for="t in typesPlantes" :key="t" :value="t">{{ t }}</option></select></div>
            <div class="form-group third full-width"><label>Type de sol favori</label><select v-model="nouvelleGraine.sol"><option value="">-- Non défini --</option><option v-for="s in typesSols" :key="s" :value="s">{{ s }}</option></select></div>
            <div class="form-group third full-width"><label>Besoin en eau *</label><select v-model="nouvelleGraine.arrosage" required><option v-for="freq in optionsArrosage" :key="freq.val" :value="freq.val">{{ freq.label }}</option></select></div>
          </div>
          
          <div class="form-row block-mobile">
            <div class="form-group flex-grow full-width">
              <label class="toggle-container mt-15">
                <input type="checkbox" v-model="nouvelleGraine.en_possession">
                <span class="toggle-slider"></span>
                <span class="toggle-label">Je possède cette graine en stock</span>
              </label>
            </div>
          </div>

          <div class="form-row block-mobile">
            <div class="form-group third full-width"><label>Début (Godet)</label><select v-model="nouvelleGraine.godet_debut"><option value="">-- Mois --</option><option v-for="m in mois" :key="'gd'+m" :value="m">{{m}}</option></select></div>
            <div class="form-group third full-width"><label>Début (Terre)</label><select v-model="nouvelleGraine.plantation_debut"><option value="">-- Mois --</option><option v-for="m in mois" :key="'ps'+m" :value="m">{{m}}</option></select></div>
            <div class="form-group third full-width"><label>Début Récolte</label><select v-model="nouvelleGraine.recolte_debut"><option value="">-- Mois --</option><option v-for="m in mois" :key="'rs'+m" :value="m">{{m}}</option></select></div>
          </div>
          <div class="form-row block-mobile">
            <div class="form-group third full-width"><label>Fin (Godet)</label><select v-model="nouvelleGraine.godet_fin"><option value="">-- Mois --</option><option v-for="m in mois" :key="'gf'+m" :value="m">{{m}}</option></select></div>
            <div class="form-group third full-width"><label>Fin (Terre)</label><select v-model="nouvelleGraine.plantation_fin"><option value="">-- Mois --</option><option v-for="m in mois" :key="'pf'+m" :value="m">{{m}}</option></select></div>
            <div class="form-group third full-width"><label>Fin Récolte</label><select v-model="nouvelleGraine.recolte_fin"><option value="">-- Mois --</option><option v-for="m in mois" :key="'rf'+m" :value="m">{{m}}</option></select></div>
          </div>
          <div class="actions"><button type="button" class="btn-cancel full-width" @click="afficherModal = false">Annuler</button><button type="submit" class="btn-submit full-width">Enregistrer</button></div>
        </form>
      </div>
    </div>
    
    <div v-if="afficherModalGodet" class="modal-overlay" @click.self="afficherModalGodet = false">
      <div class="modal">
        <h3>{{ modeEditionGodet ? 'Modifier ce godet' : 'Nouveaux semis en godet' }}</h3>
        <form @submit.prevent="validerAjoutGodet">
          <div class="form-group">
            <label>Graine à semer *</label>
            <select v-model="nouveauGodet.id_graine" required>
              <option disabled value="">-- Choisissez --</option>
              <option v-for="g in grainotheque" :key="'god'+g.id" :value="g.id">{{ g.icone }} {{ g.nom }}</option>
            </select>
          </div>
          <div class="form-group mt-15"><label>Quantité de godets *</label><input type="number" v-model="nouveauGodet.quantite" min="1" max="500" required /></div>
          <div class="form-group mt-15"><label>Emplacement (Optionnel)</label><input type="text" v-model="nouveauGodet.emplacement" placeholder="Ex: Serre, Bord de fenêtre..." /></div>
          <div class="actions block-mobile">
            <button type="button" class="btn-cancel full-width" @click="afficherModalGodet = false">Annuler</button>
            <button type="submit" class="btn-submit full-width" :disabled="!grainotheque || grainotheque.length === 0">{{ modeEditionGodet ? 'Mettre à jour' : 'Semer' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="afficherModalPlantation" class="modal-overlay" @click.self="fermerModalPlantation">
      <div class="modal">
        <h3>Planter dans ce bac</h3>
        <form @submit.prevent="validerPlantation">
          <div class="form-group">
            <label>Variété à repiquer/planter</label>
            <select v-model="nouvellePlantation.graine" required>
              <option disabled value="">-- Choisissez --</option>
              <option v-for="g in grainotheque" :key="'p'+g.id" :value="g">{{ g.icone }} {{ g.nom }}</option>
            </select>
          </div>

          <div v-if="nouvellePlantation.graine && parcelleSelectionnee && obtenirPlantesUniquesNoms(parcelleSelectionnee).length > 0">
            <div v-if="analyseAssociation?.fav?.length > 0" class="alerte-assoc box-fav">
              <span class="assoc-icon">✨</span> <div><strong>Association favorable détectée !</strong><br>Cette plante stimulera le développement avec : {{ analyseAssociation.fav.join(', ') }}</div>
            </div>
            <div v-if="analyseAssociation?.defav?.length > 0" class="alerte-assoc box-defav">
              <span class="assoc-icon">⚠️</span> <div><strong>Attention, association déconseillée.</strong><br>Évitez la proximité avec : {{ analyseAssociation.defav.join(', ') }}</div>
            </div>
          </div>

          <div class="form-group mt-15"><label>Quantité</label><input type="number" v-model="nouvellePlantation.quantite" min="1" max="1000" required /></div>
          <div class="actions block-mobile"><button type="button" class="btn-cancel full-width" @click="fermerModalPlantation">Annuler</button><button type="submit" class="btn-submit full-width">Planter</button></div>
        </form>
      </div>
    </div>

    <div v-if="afficherModalGestionBac" class="modal-overlay" @click.self="afficherModalGestionBac = false">
      <div class="modal modal-large">
        <h3>Gérer ce bac</h3>
        <div class="form-group mb-15"><label>Nom de la parcelle</label><input type="text" v-model="parcelleEnGestion.nom" @change="syncParcellesForcer" placeholder="Ex: Bac des aromates..." /></div>
        <p class="modal-desc">Modifiez les quantités, ou retirez des variétés.</p>
        <div v-if="!plantesEnGestion || plantesEnGestion.length === 0" class="etat-vide-petit">Ce bac est vide pour l'instant.</div>
        <div class="liste-gestion-plantes" v-else>
          <div v-for="(plante, i) in plantesEnGestion" :key="i" class="item-gestion block-mobile">
            <div class="item-info">
              <span class="item-icone">{{ plante.icone }}</span>
              <div class="item-details-flex">
                <span class="item-nom">{{ plante.nom }}</span>
                <input type="month" v-model="plante.date_plantation" class="input-date-petit" title="Mois de plantation" @change="syncParcellesForcer" />
              </div>
            </div>
            <div class="item-actions mt-mobile">
              <input type="number" v-model="plante.quantite" min="1" class="input-qte-petit" @change="syncParcellesForcer" />
              <button class="btn-icon rouge" @click="retirerPlanteDuBac(i)">×</button>
            </div>
          </div>
        </div>
        <div class="actions mt-30 block-mobile"><button type="button" class="btn-submit full-width" @click="afficherModalGestionBac = false">Terminer</button></div>
      </div>
    </div>

    <div v-if="afficherConfirm" class="modal-overlay" style="z-index: 9999;" @click.self="annulerConfirmation">
      <div class="modal modal-confirm">
        <div class="confirm-icon">⚠️</div>
        <h3>Confirmation</h3>
        <p class="modal-desc" style="text-align: center;">{{ confirmMessage }}</p>
        <div class="actions" style="justify-content: center;">
          <button type="button" class="btn-cancel" @click="annulerConfirmation">Annuler</button>
          <button type="button" class="btn-submit btn-danger" @click="validerConfirmation">Oui, supprimer</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import logoImg from './assets/logo.png'

const vueActive = ref('potager')
const menuReduit = ref(false)
const menuMobileOuvert = ref(false)
const parcelles = ref([])
const grainotheque = ref([])
const godets = ref([]) 

// --- NOUVEAU : SYSTEME DE CONFIRMATION GLOBALE ---
const afficherConfirm = ref(false);
const confirmMessage = ref('');
const confirmAction = ref(null);

function demanderConfirmation(msg, action) {
  confirmMessage.value = msg;
  confirmAction.value = action;
  afficherConfirm.value = true;
}

function annulerConfirmation() {
  afficherConfirm.value = false;
  confirmAction.value = null;
}

function validerConfirmation() {
  if (confirmAction.value) confirmAction.value();
  afficherConfirm.value = false;
  confirmAction.value = null;
}
// ---------------------------------------------------

function changerVue(vue) {
  vueActive.value = vue;
  menuMobileOuvert.value = false;
}

const saisonActive = ref('ete') 
const basculerSaison = () => { saisonActive.value = saisonActive.value === 'ete' ? 'hiver' : 'ete'; }

const typesPlantes = ['Légume-fruit', 'Légume-racine', 'Légume-feuille', 'Fleur compagne', 'Bulbe', 'Aromatique', 'Céréale']
const typesSols = ['Argileux (Lourd)', 'Sableux (Léger)', 'Limoneux (Riche)', 'Humifère (Terreau)', 'Calcaire', 'Tout type de sol']
const mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
const listeIcones = ['🌱','🌿','🍅','🥕','🥔','🥬','🧅','🧄','🥦','🥒','🍆','🌶️','🌽','🍓','🍈','🍉','🎃','🌼','🌻','🪻']
const listeDecos = ['🪑', '🪣', '🦆', '🦔', '🐝', '🐌', '🦉', '🦋', '🐈', '🐸', '🪵', '⛲', '🪨', '🍄', '🛒', '🚲']

const centreTerrain = 5000;
const backendUrl = ""; 

onMounted(() => {
  let link = document.querySelector("link[rel~='icon']");
  if (!link) { link = document.createElement('link'); link.rel = 'icon'; document.getElementsByTagName('head')[0].appendChild(link); }
  link.href = "data:image/svg+xml," + encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🍑</text></svg>");
});

const optionsArrosage = [{ label: 'Tous les jours (1j)', val: 1 }, { label: 'Tous les 2 jours (2j)', val: 2 }, { label: 'Tous les 3 jours (3j)', val: 3 }, { label: '1 fois par semaine (7j)', val: 7 }, { label: '1 fois toutes les 2 semaines (14j)', val: 14 }];
const getArrosageLabel = (val) => { const opt = optionsArrosage.find(o => o.val === val); return opt ? opt.label : val + 'j'; }
const getCurrentYearMonth = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`; };

const formatMoisAnnee = (yyyymm) => { 
  if (!yyyymm) return 'Date inconnue'; 
  const parts = yyyymm.split('-'); 
  if(parts.length < 2) return 'Date inconnue';
  return `${mois[parseInt(parts[1], 10) - 1]} ${parts[0]}`; 
};

const dbAssociations = [
  { plante: "Ail", fav: ["betterave", "carotte", "chou", "fraise", "laitue", "tomate"], defav: ["asperge", "haricot", "persil", "pois", "poireau", "pomme de terre"] },
  { plante: "Aubergine", fav: ["ail", "calendula", "estragon", "haricot", "laitue", "menthe", "oignon", "persil", "piment", "pois", "souci", "thym", "tomate"], defav: ["pomme de terre"] },
  { plante: "Basilic", fav: ["poivron", "tomate", "concombre", "cornichon", "courge", "melon", "chou", "fève", "courgette", "fenouil", "asperge"], defav: ["rue", "absinthe"] },
  { plante: "Bette", fav: ["oignon"], defav: ["carotte"] },
  { plante: "Betterave", fav: ["céleri", "chou", "chou-fleur", "chou-rave", "laitue", "oignon", "radis"], defav: ["asperge", "carotte", "haricot", "tomate"] },
  { plante: "Carotte", fav: ["betterave", "coriandre", "pois", "laitue", "roquette", "panais", "salsifis", "poivron", "lin", "persil", "poireau", "sauge", "tomate", "radis", "ail", "ciboulette", "échalotte", "oignon"], defav: ["fraise", "menthe", "maïs", "bette"] },
  { plante: "Céleri", fav: ["poireau", "chou"], defav: ["carotte", "maïs", "persil"] },
  { plante: "Cerfeuil", fav: ["radis", "salade", "chou-fleur", "chicorée"], defav: [] },
  { plante: "Chicorée", fav: ["epinard", "roquette", "souci", "cerfeuil"], defav: ["chou de bruxelles", "asperge", "navet"] },
  { plante: "Chou", fav: ["aneth", "betterave", "céleri", "epinard", "laitue", "haricot", "romarin", "sauge", "camomille", "géranium", "menthe", "pomme de terre"], defav: ["échalote", "fenouil", "fraise", "haricot en grain", "pâtisson", "poireau", "poivron", "radis", "tomate", "vigne"] },
  { plante: "Coriandre", fav: ["betterave", "carotte", "concombre", "chou", "pomme de terre"], defav: ["fenouil", "sauge"] },
  { plante: "Concombre", fav: ["aneth", "haricot", "laitue", "maïs", "oignon", "basilic"], defav: ["melon", "pomme de terre", "tomate", "raifort"] },
  { plante: "Courge", fav: ["asperge", "céleri", "chou", "laitue", "mâche", "pois", "oignon", "basilic", "ciboulette", "coriandre", "origan", "capucine", "tanaisie", "tournesol"], defav: ["radis", "fenouil"] },
  { plante: "Courgette", fav: ["asperge", "céleri", "chou", "laitue", "mâche", "pois", "oignon", "basilic", "ciboulette", "coriandre", "origan", "capucine", "tanaisie", "tournesol"], defav: ["radis", "fenouil"] },
  { plante: "Épinard", fav: ["aubergine", "chou", "artichaut", "chicorée", "fraisier", "fève", "haricot", "pois", "laitue", "oignon", "poireau", "radis", "fraise", "thym"], defav: ["bette", "betterave", "pomme de terre", "tomate", "poivron"] },
  { plante: "Fenouil", fav: ["céleri-rave", "poireau", "basilic"], defav: ["tomate", "absinthe", "concombre", "poivron", "épinard", "haricot", "courge", "souci", "navet", "chou", "coriandre", "carvi"] },
  { plante: "Fève", fav: ["carotte", "céleri", "chou", "pomme de terre", "maïs", "laitue", "sarriette", "basilic"], defav: ["ail", "betterave", "oignon", "poireau", "pomme de terre"] },
  { plante: "Fraise", fav: ["poireau", "thym"], defav: ["chou"] },
  { plante: "Haricot", fav: ["maïs", "potiron", "chou", "melon", "pastèque", "carotte", "céleri", "concombre", "pomme de terre", "épinard", "laitue", "bourrache", "capucine", "sarriette", "tournesol", "absinthe"], defav: ["poireau", "ail", "échalote", "oignon", "ciboulette", "fenouil", "pois", "courgette"] },
  { plante: "Laitue", fav: ["chou", "carotte", "oignon", "cardon", "pois", "betterave", "bette", "courge", "fève", "fraisier", "melon", "haricot", "navet", "poireau", "artichaut", "cerfeuil", "aneth", "lin"], defav: ["maïs", "panais"] },
  { plante: "Mâche", fav: ["chou", "oignon", "poireau"], defav: ["amaranthe"] },
  { plante: "Maïs", fav: ["betterave", "haricot", "pois", "potiron", "tournesol"], defav: ["laitue", "oignon"] },
  { plante: "Melon", fav: ["laitue", "basilic", "haricot", "pastèque"], defav: ["concombre"] },
  { plante: "Navet", fav: ["laitue", "menthe", "pois", "romarin"], defav: ["ail"] },
  { plante: "Oignon", fav: ["betterave", "camomille", "carotte", "fenouil", "fraise", "laitue", "mâche", "radis", "tomate", "chou", "pomme de terre"], defav: ["chou", "fève", "haricot", "maïs", "persil", "poireau", "pois"] },
  { plante: "Panais", fav: ["radis", "betterave", "chou-rave", "oignon"], defav: ["aneth", "laitue"] },
  { plante: "Persil", fav: ["radis", "tomate", "rosier", "artichaut", "asperge"], defav: ["céleri", "pois", "laitue", "poireau"] },
  { plante: "Piment", fav: ["basilic", "carotte", "livèche", "marjolaine", "tomate", "aubergine", "oignon"], defav: ["fenouil", "chou-rave", "patate douce", "haricot"] },
  { plante: "Poivron", fav: ["basilic", "carotte", "livèche", "marjolaine", "tomate", "aubergine", "oignon"], defav: ["fenouil", "chou-rave", "patate douce", "haricot"] },
  { plante: "Pomme de terre", fav: ["bourrache", "chou", "coriandre", "échalote", "fève", "haricot", "laitue", "œillet", "pois", "radis", "souci"], defav: ["tournesol", "maïs", "ail", "oignon"] },
  { plante: "Poireau", fav: ["carotte", "céleri", "fraise", "tomate", "asperge", "laitue", "mâche", "fenouil", "artichaut", "moutarde", "cresson"], defav: ["bette", "betterave", "chou", "haricot", "persil", "pois"] },
  { plante: "Pois", fav: ["pomme de terre", "coriandre", "ricin", "chou", "céleri", "carotte", "asperge", "laitue", "radis", "haricot", "maïs", "navet", "courge", "concombre", "tournesol", "carvi", "sarriette"], defav: ["ail", "échalote", "oignon", "persil", "poireau", "ciboulette"] },
  { plante: "Radis", fav: ["cresson", "cerfeuil", "panais", "carotte", "pois", "concombre", "cornichon", "épinard", "haricot", "céleri-rave", "pomme de terre", "tomate", "oignon"], defav: ["chou", "ciboulette", "courgette", "tournesol", "sarriette"] },
  { plante: "Tomate", fav: ["aneth", "basilic", "persil", "carotte", "céleri", "cosmos", "camomille", "chou", "oeillet", "pastèque", "concombre", "radis", "tétragone", "capucine", "maïs"], defav: ["fenouil", "tournesol", "betterave", "bette", "pois", "chou-rave"] }
];

const rotationCategories = [
  { id: 'legumineuses', nom: 'Légumineuses (Graines)', desc: 'Elles captent l\'azote de l\'air pour enrichir la terre. C\'est le point de départ idéal.', plantes: ["Fève", "Haricot", "Pois"] },
  { id: 'feuilles', nom: 'Légumes-Feuilles', desc: 'Ils profitent de l\'azote abondant laissé par les légumineuses l\'année précédente.', plantes: ["Basilic", "Bette", "Céleri", "Cerfeuil", "Chicorée", "Chou", "Coriandre", "Épinard", "Fenouil", "Laitue", "Mâche", "Persil", "Poireau"] },
  { id: 'racines', nom: 'Légumes-Racines & Bulbes', desc: 'Ils puisent le reste des nutriments en profondeur et ameublissent le sol.', plantes: ["Ail", "Betterave", "Carotte", "Navet", "Oignon", "Panais", "Pomme de terre", "Radis"] },
  { id: 'fruits', nom: 'Légumes-Fruits', desc: 'Très gourmands ! Ils nécessitent souvent un ajout de compost avant d\'être plantés.', plantes: ["Aubergine", "Concombre", "Courge", "Courgette", "Fraise", "Maïs", "Melon", "Piment", "Poivron", "Tomate"] }
];

const enrichissementSaisons = [
  { saison: 'Printemps', icone: '🌱', texte: 'Apport de compost mûr et de fumier composté. Idéal pour préparer la terre des légumes gourmands (Légumes-Fruits).' },
  { saison: 'Été', icone: '☀️', texte: 'Paillage (tonte séchée, paille) pour nourrir le sol en surface et retenir l\'eau. Apport de purin (ortie, consoude) pour booster la croissance.' },
  { saison: 'Automne', icone: '🍂', texte: 'Épandage de compost demi-mûr ou fumier frais en surface (sans enfouir). Couverture avec un épais paillis de feuilles mortes.' },
  { saison: 'Hiver', icone: '❄️', texte: 'Semis d\'engrais verts (moutarde, phacélie) sur les parcelles vides. Ne laissez jamais un sol nu pour protéger la vie microbienne.' }
];

const besoinsFamilles = [
  { plante: 'Tomate, Aubergine, Poivron', type: 'fruits', labelType: 'Légumes-Fruits', arrosage: '💦 Abondant (au pied)', saison: '☀️ Été', soleil: '☀️ Plein soleil', plantation: 'Mai - Juin' },
  { plante: 'Courge, Courgette, Melon', type: 'fruits', labelType: 'Légumes-Fruits', arrosage: '💦 Très abondant', saison: '☀️ Été', soleil: '☀️ Plein soleil', plantation: 'Mai' },
  { plante: 'Fraise', type: 'fruits', labelType: 'Petits Fruits', arrosage: '💧 Régulier', saison: '🌱 Printemps / ☀️ Été', soleil: '☀️ Soleil / ⛅ Mi-ombre', plantation: 'Sept-Oct / Mars-Avril' },
  { plante: 'Laitue, Épinard, Mâche', type: 'feuilles', labelType: 'Légumes-Feuilles', arrosage: '💧 Régulier (craint le sec)', saison: '🌱 Printemps / 🍂 Automne', soleil: '⛅ Mi-ombre', plantation: 'Mars - Septembre' },
  { plante: 'Chou, Brocoli, Chou-fleur', type: 'feuilles', labelType: 'Légumes-Feuilles', arrosage: '💦 Abondant', saison: '❄️ Toute l\'année', soleil: '☀️ Soleil / ⛅ Mi-ombre', plantation: 'Mars - Août' },
  { plante: 'Aromatiques (Basilic, Persil...)', type: 'feuilles', labelType: 'Aromatiques', arrosage: '🌱 Modéré à faible', saison: '☀️ Été', soleil: '☀️ Soleil / ⛅ Mi-ombre', plantation: 'Avril - Mai' },
  { plante: 'Carotte, Panais', type: 'racines', labelType: 'Légumes-Racines', arrosage: '🌱 Faible à modéré', saison: '☀️ Été / 🍂 Automne', soleil: '☀️ Plein soleil', plantation: 'Mars - Juillet' },
  { plante: 'Radis, Navet', type: 'racines', labelType: 'Légumes-Racines', arrosage: '💧 Régulier (évite le piquant)', saison: '🌱 Printemps / 🍂 Automne', soleil: '⛅ Mi-ombre / ☀️ Soleil', plantation: 'Mars - Septembre' },
  { plante: 'Ail, Oignon, Échalote', type: 'racines', labelType: 'Bulbes', arrosage: '🌵 Très faible (craint l\'eau)', saison: '☀️ Été', soleil: '☀️ Plein soleil', plantation: 'Fév-Mars / Oct-Nov' },
  { plante: 'Pomme de terre', type: 'racines', labelType: 'Tubercules', arrosage: '💧 Modéré', saison: '☀️ Été / 🍂 Automne', soleil: '☀️ Plein soleil', plantation: 'Mars - Mai' },
  { plante: 'Haricot, Pois, Fève', type: 'legumineuses', labelType: 'Légumineuses', arrosage: '💧 Régulier (surtout floraison)', saison: '🌱 Printemps / ☀️ Été', soleil: '☀️ Plein soleil', plantation: 'Fév - Juillet' }
];

const rechercheConseil = ref('');
const conseilsFiltres = computed(() => { if(!rechercheConseil.value) return dbAssociations; return dbAssociations.filter(a => (a.plante || '').toLowerCase().includes((rechercheConseil.value || '').toLowerCase())); });

function normaliserTexte(str) { return (str || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim(); }

function verifierLien(planteA, planteB) { 
  const normA = normaliserTexte(planteA); const normB = normaliserTexte(planteB); 
  const objA = dbAssociations.find(a => normaliserTexte(a.plante).includes(normA) || normA.includes(normaliserTexte(a.plante))); 
  const objB = dbAssociations.find(b => normaliserTexte(b.plante).includes(normB) || normB.includes(normaliserTexte(b.plante))); 
  let isFav = false; let isDefav = false; 
  if (objA?.fav) { 
    if (objA.fav.some(f => normB.includes(normaliserTexte(f)) || normaliserTexte(f).includes(normB))) isFav = true; 
    if (objA.defav?.some(f => normB.includes(normaliserTexte(f)) || normaliserTexte(f).includes(normB))) isDefav = true; 
  } 
  if (objB?.fav) { 
    if (objB.fav.some(f => normA.includes(normaliserTexte(f)) || normaliserTexte(f).includes(normA))) isFav = true; 
    if (objB.defav?.some(f => normA.includes(normaliserTexte(f)) || normaliserTexte(f).includes(normA))) isDefav = true; 
  } 
  return { isFav, isDefav }; 
}

function aConflit(parcelle) { 
  if (!parcelle || parcelle.type !== 'bac') return false; 
  const plantations = saisonActive.value === 'ete' ? (parcelle.plantations_ete || []) : (parcelle.plantations_hiver || []); 
  const noms = [...new Set(plantations.map(p => p.nom))]; 
  for (let i = 0; i < noms.length; i++) { 
    for (let j = i + 1; j < noms.length; j++) { 
      if (verifierLien(noms[i], noms[j]).isDefav) return true; 
    } 
  } 
  return false; 
}

function obtenirPlantesUniquesNoms(parcelle) { 
  if (!parcelle || parcelle.type !== 'bac') return []; 
  const plantations = saisonActive.value === 'ete' ? (parcelle.plantations_ete || []) : (parcelle.plantations_hiver || []); 
  return [...new Set(plantations.map(p => p.nom))]; 
}

const analyseAssociation = computed(() => { 
  let favs = []; let defavs = []; 
  if (!parcelleSelectionnee.value || !nouvellePlantation.value.graine) return { fav: [], defav: [] }; 
  const cibleNom = nouvellePlantation.value.graine.nom; 
  const existantes = obtenirPlantesUniquesNoms(parcelleSelectionnee.value); 
  existantes.forEach(nom => { 
    const res = verifierLien(cibleNom, nom); 
    if (res?.isFav) favs.push(nom); 
    if (res?.isDefav) defavs.push(nom); 
  }); 
  return { fav: [...new Set(favs)], defav: [...new Set(defavs)] }; 
});

const rechercheGraine = ref(''); const filtreTypeGraine = ref(''); const filtrePossession = ref(false); 
const grainesFiltrees = computed(() => { 
  if (!grainotheque.value) return []; 
  return grainotheque.value.filter(g => { 
    const matchNom = (g.nom || '').toLowerCase().includes((rechercheGraine.value || '').toLowerCase()); 
    const matchType = filtreTypeGraine.value === '' || g.type === filtreTypeGraine.value; 
    const matchPossession = !filtrePossession.value || g.en_possession; 
    return matchNom && matchType && matchPossession; 
  }); 
});

const afficherModalGodet = ref(false); const modeEditionGodet = ref(false); const nouveauGodet = ref({ id_graine: '', quantite: 1, emplacement: '' });
function ouvrirModalAjoutGodet(g = null) { if (g) { modeEditionGodet.value = true; nouveauGodet.value = { ...g }; } else { modeEditionGodet.value = false; nouveauGodet.value = { id_graine: '', quantite: 1, emplacement: '' }; } afficherModalGodet.value = true; };
function validerAjoutGodet() { if (modeEditionGodet.value) { const index = godets.value.findIndex(g => g.id === nouveauGodet.value.id); if (index !== -1) godets.value[index] = { ...nouveauGodet.value }; } else { godets.value.push({ id: Date.now(), ...nouveauGodet.value }); } afficherModalGodet.value = false; };
function supprimerGodet(id) {
  demanderConfirmation("Confirmez-vous le repiquage ou la suppression de ce godet ?", () => {
    godets.value = godets.value.filter(g => g.id !== id);
  });
}
function estEnGodet(idGraine) { return (godets.value || []).some(g => g.id_graine === idGraine); };
const godetsAffichables = computed(() => { if (!godets.value) return []; return godets.value.map(godet => { const graine = (grainotheque.value || []).find(g => g.id === godet.id_graine) || { nom: 'Graine supprimée', icone: '❓', type: 'Inconnu' }; return { ...godet, nom: graine.nom, icone: graine.icone, type: graine.type }; }).reverse(); });
const totalGodetsCultives = computed(() => (godets.value || []).reduce((acc, g) => acc + g.quantite, 0));

function debounce(fn, delay) { let timeoutId; return (...args) => { clearTimeout(timeoutId); timeoutId = setTimeout(() => fn(...args), delay); }; }
const syncGraines = debounce(async (data) => { localStorage.setItem('mySecretGarden_graines', JSON.stringify(data)); try { await fetch(`${backendUrl}/api/graines`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); } catch(e){} }, 1000);
const syncParcelles = debounce(async (data) => { localStorage.setItem('mySecretGarden_parcelles', JSON.stringify(data)); try { await fetch(`${backendUrl}/api/parcelles`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); } catch(e){} }, 1000);
const syncGodets = debounce(async (data) => { localStorage.setItem('mySecretGarden_godets', JSON.stringify(data)); try { await fetch(`${backendUrl}/api/godets`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); } catch(e){} }, 1000);
function syncParcellesForcer() { syncParcelles(parcelles.value); }

watch(grainotheque, (newVal) => { syncGraines(newVal); }, { deep: true });
watch(parcelles, (newVal) => { syncParcelles(newVal); }, { deep: true });
watch(godets, (newVal) => { syncGodets(newVal); }, { deep: true });

const reglages = ref({ webhookUrl: '', webhookArrosage: true, webhookPluie: true, webhookHeure: '10:00', ville: '' });
const syncReglagesServeur = debounce(async (data) => { try { await fetch(`${backendUrl}/api/reglages`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); } catch(e){} }, 1000);
watch(reglages, (newVal) => { syncReglagesServeur(newVal); }, { deep: true });

onMounted(async () => {
  try { const resGraines = await fetch(`${backendUrl}/api/graines`); if (resGraines.ok) grainotheque.value = await resGraines.json(); } catch(e) { const saved = localStorage.getItem('mySecretGarden_graines'); if(saved) grainotheque.value = JSON.parse(saved) || []; }
  try { 
    const resParcelles = await fetch(`${backendUrl}/api/parcelles`); 
    if (resParcelles.ok) {
      let dataParcelles = await resParcelles.json();
      dataParcelles.forEach(p => { 
        if (!p.type) p.type = 'bac';
        if (p.type === 'bac') {
            if (!p.plantations_ete) p.plantations_ete = p.plantations || []; 
            if (!p.plantations_hiver) p.plantations_hiver = []; 
            if (!p.archives) p.archives = [];
            if (!p.dernier_arrosage) p.dernier_arrosage = Date.now(); 
        }
        if (!p.nom) p.nom = ''; 
        p.arrosageEnCours = false; 
        delete p.plantations; 
      });
      parcelles.value = dataParcelles;
    }
  } catch(e) { const saved = localStorage.getItem('mySecretGarden_parcelles'); if(saved) parcelles.value = JSON.parse(saved) || []; }
  
  try { const resGodets = await fetch(`${backendUrl}/api/godets`); if (resGodets.ok) godets.value = await resGodets.json(); } catch(e) { const saved = localStorage.getItem('mySecretGarden_godets'); if(saved) godets.value = JSON.parse(saved) || []; }
  try { const resReg = await fetch(`${backendUrl}/api/reglages`); if (resReg.ok) { const dataReg = await resReg.json(); reglages.value = { ...reglages.value, ...dataReg }; } } catch(e) { const saved = localStorage.getItem('mySecretGarden_reglages'); if(saved) reglages.value = { ...reglages.value, ...JSON.parse(saved) }; }
  
  if (reglages.value.ville) chargerMeteo();
});

const meteoInfo = ref(null); const meteoErreur = ref(false);
async function chargerMeteo() {
  if (!reglages.value.ville) { meteoErreur.value = false; meteoInfo.value = null; return; }
  try {
    const searchString = encodeURIComponent(reglages.value.ville.trim());
    const geoRes = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${searchString}&count=1&language=fr`); 
    const geoData = await geoRes.json();
    if (!geoData.results || geoData.results.length === 0) { meteoErreur.value = true; meteoInfo.value = null; return; }
    const { latitude, longitude, name } = geoData.results[0];
    const wRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&current_weather=true&timezone=auto`);
    const wData = await wRes.json();
    meteoInfo.value = wData; meteoInfo.value.cityName = name; meteoErreur.value = false;
  } catch (e) { meteoErreur.value = true; meteoInfo.value = null; }
}

function getWeatherEmoji(code) { if(code === 0) return '☀️'; if(code > 0 && code < 4) return '⛅'; if(code > 44 && code < 49) return '🌫️'; if(code > 50 && code < 68) return '🌧️'; if(code > 70 && code < 80) return '❄️'; if(code > 94) return '⛈️'; return '🌤️'; }
function formatJour(dateStr) { return new Date(dateStr).toLocaleDateString('fr-FR', { weekday: 'short' }); }

function bacBesoinEau(bac) {
  if (!bac || bac.type !== 'bac') return false;
  const saison = saisonActive.value === 'ete' ? 'plantations_ete' : 'plantations_hiver';
  if (!bac[saison] || bac[saison].length === 0) return false;
  let minFreq = 999;
  bac[saison].forEach(plant => { const g = (grainotheque.value || []).find(x => x.id === plant.id_graine); if (g && g.arrosage < minFreq) minFreq = g.arrosage; });
  if (minFreq === 999) minFreq = 7; 
  return ((Date.now() - (bac.dernier_arrosage || 0)) / (1000 * 3600 * 24)) >= minFreq;
}

function arroserBac(bac) { bac.arrosageEnCours = true; bac.dernier_arrosage = Date.now(); setTimeout(() => { bac.arrosageEnCours = false; syncParcellesForcer(); }, 2000); }
const pluieGlobaleActive = ref(false);
function arroserTout() {
  pluieGlobaleActive.value = true;
  (parcelles.value || []).forEach(p => { 
    if (p.type === 'bac' && bacBesoinEau(p)) { p.arrosageEnCours = true; p.dernier_arrosage = Date.now(); }
  });
  setTimeout(() => { pluieGlobaleActive.value = false; (parcelles.value || []).forEach(p => p.arrosageEnCours = false); syncParcellesForcer(); }, 2500);
}
function declencherArrosageGlobal() { arroserTout(); }

const alertesArrosage = computed(() => {
  if (!parcelles.value) return [];
  return parcelles.value.filter(p => bacBesoinEau(p)).map(p => { 
    const saison = saisonActive.value === 'ete' ? 'plantations_ete' : 'plantations_hiver';
    const plantesDuBac = p[saison] ? [...new Set(p[saison].map(pl => pl.nom))] : [];
    return { id: p.id, bac: p, nom: p.nom, plantes: plantesDuBac, joursDepuis: Math.floor((Date.now() - (p.dernier_arrosage || 0)) / (1000 * 3600 * 24)) }; 
  }); 
});

const alertesSaisonsFiltrees = computed(() => {
  if (!grainotheque.value) return [];
  const currentMonthIdx = new Date().getMonth();
  const getMoisDistance = (moisNom) => { 
    if(!moisNom) return 99; 
    const idx = mois.indexOf(moisNom); 
    if(idx === -1) return 99; 
    return (idx - currentMonthIdx + 12) % 12; 
  };
  let alertes = [];
  grainotheque.value.forEach(g => {
    if(g.godet_debut) { const dist = getMoisDistance(g.godet_debut); if(dist >= 0 && dist <= 1) alertes.push({ type: 'godet', plante: g.nom, icone: g.icone, dist: dist, mois: g.godet_debut }); }
    if(g.plantation_debut) { const dist = getMoisDistance(g.plantation_debut); if(dist >= 0 && dist <= 1) alertes.push({ type: 'semis', plante: g.nom, icone: g.icone, dist: dist, mois: g.plantation_debut }); }
  });
  return alertes.sort((a,b) => a.dist - b.dist);
});
const totalAlertes = computed(() => { return (alertesArrosage.value ? alertesArrosage.value.length : 0) + (alertesSaisonsFiltrees.value ? alertesSaisonsFiltrees.value.length : 0); });

async function testerWebhookDiscord() {
  if (!reglages.value.webhookUrl) return;
  try {
    await fetch(`${backendUrl}/api/reglages`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(reglages.value) });
    const res = await fetch(`${backendUrl}/api/test-webhook`, { method: 'POST' });
    if(res.ok) alert('Webhook de test envoyé avec succès ! Vérifiez votre serveur Discord.');
    else alert("Erreur du serveur lors du test.");
  } catch (e) {
    alert('Erreur lors de l\'envoi du webhook de test. Vérifiez votre URL ou votre bloqueur de publicité.');
  }
}

const zoom = ref(1); function zoomer(delta) { zoom.value = Math.min(Math.max(0.2, zoom.value + delta), 3); } function gererZoom(e) { if (e.deltaY < 0) zoomer(0.05); else zoomer(-0.05); }

const outilActif = ref('main'); const terrainRef = ref(null); const pan = ref({ x: 0, y: 0 }); const isPanning = ref(false); const lastMousePos = ref({ x: 0, y: 0 }); const enTrainDeDessiner = ref(false); const pointDepart = ref({ x: 0, y: 0 }); const parcelleEnCours = ref(null); const draggedParcelle = ref(null); const resizingParcelle = ref(null); const dragOffset = ref({ x: 0, y: 0 }); const pixelsParMetre = 40; const pixelsPar10cm = 4;

function styleTerrainElement(p) { 
  if (p.type === 'bordure') {
    const length = Math.hypot(p.x2 - p.x1, p.y2 - p.y1);
    const angle = Math.atan2(p.y2 - p.y1, p.x2 - p.x1) * (180 / Math.PI);
    return { left: p.x1 + 'px', top: p.y1 + 'px', width: length + 'px', transform: `rotate(${angle}deg)` };
  } else if (p.type === 'arbre' || p.type === 'deco') {
    return { left: p.x + 'px', top: p.y + 'px' };
  } else {
    return { left: p.x + 'px', top: p.y + 'px', width: p.width + 'px', height: p.height + 'px' }; 
  }
}

function styleTooltip(p) {
  if (p.type === 'bordure') {
    const angle = Math.atan2(p.y2 - p.y1, p.x2 - p.x1) * (180 / Math.PI);
    return { transform: `translateX(-50%) rotate(${-angle}deg)` };
  }
  return {};
}

function recentrerTerrain() { pan.value = { x: 0, y: 0 }; zoom.value = 1; } 
function allerAuBac(bac) { if(!bac) return; pan.value = { x: -bac.x + (window.innerWidth/2) - 140, y: -bac.y + (window.innerHeight/2) }; zoom.value = 1.2; vueActive.value = 'potager'; menuMobileOuvert.value = false; }

function supprimerParcelle(id) { 
  demanderConfirmation("Voulez-vous vraiment supprimer cet élément du terrain ?", () => {
    parcelles.value = parcelles.value.filter(p => p.id !== id); 
    if(parcelleHistoriqueSelectionnee.value?.id === id) fermerHistorique(); 
    syncParcellesForcer();
  });
}

const afficherModalArbre = ref(false);
const afficherModalDeco = ref(false);
const nouvelleCibleCoords = ref({x: 0, y: 0});
const nouvelArbre = ref({ nom: '', taille: 'Moyen' });
const nouvelleDeco = ref({ icone: '' });

function getEvtCoords(e) { if (e.touches && e.touches.length > 0) return { x: e.touches[0].clientX, y: e.touches[0].clientY }; return { x: e.clientX, y: e.clientY }; }

function commencerAction(e) { 
  const coords = getEvtCoords(e); 
  const rect = terrainRef.value.getBoundingClientRect(); 
  const rawX = (coords.x - rect.left) / zoom.value;
  const rawY = (coords.y - rect.top) / zoom.value;
  const snappedX = Math.round(rawX / pixelsPar10cm) * pixelsPar10cm;
  const snappedY = Math.round(rawY / pixelsPar10cm) * pixelsPar10cm;

  if (outilActif.value === 'main') { 
    isPanning.value = true; 
    lastMousePos.value = { x: coords.x, y: coords.y };
  } else if (outilActif.value === 'arbre') {
    nouvelleCibleCoords.value = { x: snappedX, y: snappedY };
    nouvelArbre.value = { nom: '', taille: 'Moyen' };
    afficherModalArbre.value = true;
    outilActif.value = 'main';
  } else if (outilActif.value === 'deco') {
    nouvelleCibleCoords.value = { x: snappedX, y: snappedY };
    nouvelleDeco.value = { icone: '' };
    afficherModalDeco.value = true;
    outilActif.value = 'main';
  } else if (outilActif.value === 'bordure') {
    enTrainDeDessiner.value = true; 
    pointDepart.value = { x: rawX, y: rawY }; 
    parcelleEnCours.value = { type: 'bordure', x1: rawX, y1: rawY, x2: rawX, y2: rawY }; 
  } else if (outilActif.value === 'bac') {
    enTrainDeDessiner.value = true; 
    pointDepart.value = { x: rawX, y: rawY }; 
    parcelleEnCours.value = { type: 'bac', nom: '', x: rawX, y: rawY, width: 0, height: 0, dimX: 0, dimY: 0, plantations_ete: [], plantations_hiver: [], dernier_arrosage: Date.now() }; 
  } 
}

function validerAjoutArbre() {
  parcelles.value.push({
    id: Date.now(), type: 'arbre', taille: nouvelArbre.value.taille, nom: nouvelArbre.value.nom,
    x: nouvelleCibleCoords.value.x, y: nouvelleCibleCoords.value.y,
    plantations_ete: [], plantations_hiver: [], dernier_arrosage: Date.now()
  });
  afficherModalArbre.value = false;
}

function validerAjoutDeco() {
  parcelles.value.push({
    id: Date.now(), type: 'deco', icone: nouvelleDeco.value.icone,
    x: nouvelleCibleCoords.value.x, y: nouvelleCibleCoords.value.y
  });
  afficherModalDeco.value = false;
}

function commencerDragParcelle(e, p) { 
  if (outilActif.value !== 'main') return; 
  draggedParcelle.value = p; 
  const coords = getEvtCoords(e); 
  const rect = terrainRef.value.getBoundingClientRect(); 
  const rawX = (coords.x - rect.left) / zoom.value;
  const rawY = (coords.y - rect.top) / zoom.value;
  if (p.type === 'bordure') {
    dragOffset.value = { x: rawX - p.x1, y: rawY - p.y1 };
  } else {
    dragOffset.value = { x: rawX - p.x, y: rawY - p.y };
  }
}

const resizeBordureTarget = ref(null);
function commencerResize(e, p) { 
  if (p.type === 'bordure') {
    resizeBordureTarget.value = { p, handle: 'end' }; 
  } else {
    resizingParcelle.value = p; 
    const coords = getEvtCoords(e); 
    const rect = terrainRef.value.getBoundingClientRect(); 
    pointDepart.value = { x: (coords.x - rect.left) / zoom.value, y: (coords.y - rect.top) / zoom.value, w: p.width, h: p.height }; 
  }
}

function actionEnCours(e) { 
  const coords = getEvtCoords(e); 
  const rect = terrainRef.value.getBoundingClientRect(); 
  let mouseX = (coords.x - rect.left) / zoom.value; 
  let mouseY = (coords.y - rect.top) / zoom.value; 

  if (isPanning.value) { 
    pan.value.x += coords.x - lastMousePos.value.x; 
    pan.value.y += coords.y - lastMousePos.value.y; 
    lastMousePos.value = { x: coords.x, y: coords.y };
  } else if (resizingParcelle.value && resizingParcelle.value.type === 'bac') { 
    let rawWidth = pointDepart.value.w + (mouseX - pointDepart.value.x); 
    let rawHeight = pointDepart.value.h + (mouseY - pointDepart.value.y); 
    let snappedWidth = Math.max(40, Math.round(rawWidth / pixelsPar10cm) * pixelsPar10cm); 
    let snappedHeight = Math.max(40, Math.round(rawHeight / pixelsPar10cm) * pixelsPar10cm); 
    resizingParcelle.value.width = snappedWidth; 
    resizingParcelle.value.height = snappedHeight; 
    resizingParcelle.value.dimX = Math.round((snappedWidth / pixelsParMetre) * 100); 
    resizingParcelle.value.dimY = Math.round((snappedHeight / pixelsParMetre) * 100); 
  } else if (resizeBordureTarget.value) {
    resizeBordureTarget.value.p.x2 = Math.round(mouseX / pixelsPar10cm) * pixelsPar10cm;
    resizeBordureTarget.value.p.y2 = Math.round(mouseY / pixelsPar10cm) * pixelsPar10cm;
  } else if (draggedParcelle.value) { 
    let rawX = mouseX - dragOffset.value.x; 
    let rawY = mouseY - dragOffset.value.y; 
    let snappedX = Math.round(rawX / pixelsPar10cm) * pixelsPar10cm; 
    let snappedY = Math.round(rawY / pixelsPar10cm) * pixelsPar10cm;
    
    if (draggedParcelle.value.type === 'bordure') {
      const dx = snappedX - draggedParcelle.value.x1;
      const dy = snappedY - draggedParcelle.value.y1;
      draggedParcelle.value.x1 += dx;
      draggedParcelle.value.y1 += dy;
      draggedParcelle.value.x2 += dx;
      draggedParcelle.value.y2 += dy;
    } else {
      draggedParcelle.value.x = snappedX; 
      draggedParcelle.value.y = snappedY;
    }
  } else if (enTrainDeDessiner.value) { 
    if (parcelleEnCours.value.type === 'bordure') {
      parcelleEnCours.value.x2 = mouseX;
      parcelleEnCours.value.y2 = mouseY;
    } else {
      let rawWidth = mouseX - pointDepart.value.x; 
      let rawHeight = mouseY - pointDepart.value.y; 
      let originX = pointDepart.value.x; 
      let originY = pointDepart.value.y; 
      if (rawWidth < 0) { originX = mouseX; rawWidth = Math.abs(rawWidth); } 
      if (rawHeight < 0) { originY = mouseY; rawHeight = Math.abs(rawHeight); } 
      const snappedWidth = Math.max(40, Math.round(rawWidth / pixelsPar10cm) * pixelsPar10cm); 
      const snappedHeight = Math.max(40, Math.round(rawHeight / pixelsPar10cm) * pixelsPar10cm); 
      parcelleEnCours.value.x = originX;
      parcelleEnCours.value.y = originY;
      parcelleEnCours.value.width = snappedWidth;
      parcelleEnCours.value.height = snappedHeight;
      parcelleEnCours.value.dimX = Math.round((snappedWidth / pixelsParMetre) * 100); 
      parcelleEnCours.value.dimY = Math.round((snappedHeight / pixelsParMetre) * 100);
    }
  } 
}

function terminerAction() { 
  isPanning.value = false; draggedParcelle.value = null; resizingParcelle.value = null; resizeBordureTarget.value = null;
  if (enTrainDeDessiner.value) { 
    enTrainDeDessiner.value = false; 
    if (parcelleEnCours.value.type === 'bordure') {
      const dist = Math.hypot(parcelleEnCours.value.x2 - parcelleEnCours.value.x1, parcelleEnCours.value.y2 - parcelleEnCours.value.y1);
      if (dist > 10) parcelles.value.push({ ...parcelleEnCours.value, id: Date.now() });
    } else if (parcelleEnCours.value.type === 'bac' && parcelleEnCours.value.dimX >= 20 && parcelleEnCours.value.dimY >= 20) { 
      parcelles.value.push({ ...parcelleEnCours.value, id: Date.now() });
    }
    parcelleEnCours.value = null; 
    outilActif.value = 'main'; 
  } 
}

const afficherModal = ref(false); const modeEdition = ref(false); const graineParDefaut = { id: null, nom: '', type: 'Légume-fruit', icone: '🌱', sol: '', arrosage: 7, godet_debut: '', godet_fin: '', plantation_debut: '', plantation_fin: '', recolte_debut: '', recolte_fin: '', en_possession: true }; const nouvelleGraine = ref({ ...graineParDefaut }); 
function ouvrirModalGraine(g = null) { if (g) { modeEdition.value = true; nouvelleGraine.value = { ...g }; } else { modeEdition.value = false; nouvelleGraine.value = { ...graineParDefaut }; } afficherModal.value = true; }
function sauvegarderGraine() { if (modeEdition.value) { const index = grainotheque.value.findIndex(g => g.id === nouvelleGraine.value.id); if (index !== -1) grainotheque.value[index] = { ...nouvelleGraine.value }; } else { nouvelleGraine.value.id = Date.now(); if(!grainotheque.value) grainotheque.value = []; grainotheque.value.push({ ...nouvelleGraine.value }); } afficherModal.value = false; }
function supprimerGraine(id) { 
  demanderConfirmation("Supprimer cette variété de l'encyclopédie ? (Vos godets existants ne seront pas impactés)", () => {
    grainotheque.value = grainotheque.value.filter(g => g.id !== id);
  });
}

const afficherModalPlantation = ref(false); const parcelleSelectionnee = ref(null); const nouvellePlantation = ref({ graine: '', quantite: 1 }); 
function ouvrirModalPlantation(parcelle) { if (!grainotheque.value || grainotheque.value.length === 0) { alert("Ajoutez des graines d'abord !"); return; } parcelleSelectionnee.value = parcelle; nouvellePlantation.value = { graine: '', quantite: 1 }; afficherModalPlantation.value = true; }
function fermerModalPlantation() { afficherModalPlantation.value = false; parcelleSelectionnee.value = null; }
function validerPlantation() { if (parcelleSelectionnee.value && nouvellePlantation.value.graine) { const saison = saisonActive.value === 'ete' ? 'plantations_ete' : 'plantations_hiver'; if (!parcelleSelectionnee.value[saison]) parcelleSelectionnee.value[saison] = []; parcelleSelectionnee.value[saison].push({ id_graine: nouvellePlantation.value.graine.id, nom: nouvellePlantation.value.graine.nom, icone: nouvellePlantation.value.graine.icone, quantite: nouvellePlantation.value.quantite, date_plantation: getCurrentYearMonth() }); parcelleSelectionnee.value.dernier_arrosage = Date.now(); syncParcellesForcer(); fermerModalPlantation(); } }

const afficherModalGestionBac = ref(false); const plantesEnGestion = ref([]); const parcelleEnGestion = ref(null); 
function ouvrirModalGestionBac(parcelle) { parcelleEnGestion.value = parcelle; const saison = saisonActive.value === 'ete' ? 'plantations_ete' : 'plantations_hiver'; plantesEnGestion.value = parcelle[saison] || []; plantesEnGestion.value.forEach(p => { if(!p.date_plantation) p.date_plantation = getCurrentYearMonth(); }); afficherModalGestionBac.value = true; }

function retirerPlanteDuBac(index) { 
  demanderConfirmation("Retirer cette plante du bac ? (Elle sera conservée dans l'historique des récoltes)", () => {
    const planteCible = plantesEnGestion.value[index];
    if (!parcelleEnGestion.value.archives) parcelleEnGestion.value.archives = [];
    parcelleEnGestion.value.archives.push({
      ...planteCible,
      saison: saisonActive.value,
      date_retrait: getCurrentYearMonth()
    });
    plantesEnGestion.value.splice(index, 1); 
    syncParcellesForcer();
  });
}

const parcelleHistoriqueSelectionnee = ref(null); 
function ouvrirHistorique(parcelle) { parcelleHistoriqueSelectionnee.value = parcelle; }
function fermerHistorique() { parcelleHistoriqueSelectionnee.value = null; }

const historiqueParcelle = computed(() => { 
  if (!parcelleHistoriqueSelectionnee.value) return []; 
  const p = parcelleHistoriqueSelectionnee.value; 
  const toutesPlantations = []; 
  
  if (p.plantations_ete) p.plantations_ete.forEach(pl => toutesPlantations.push({...pl, saison: 'ete', active: true})); 
  if (p.plantations_hiver) p.plantations_hiver.forEach(pl => toutesPlantations.push({...pl, saison: 'hiver', active: true})); 
  if (p.archives) p.archives.forEach(pl => toutesPlantations.push({...pl, active: false}));

  toutesPlantations.sort((a, b) => { 
    const dateA = a.date_plantation || '1970-01'; 
    const dateB = b.date_plantation || '1970-01'; 
    return dateB.localeCompare(dateA); 
  }); 

  const groupes = []; 
  let currentGroup = null; 
  toutesPlantations.forEach(pl => { 
    const d = pl.date_plantation || ''; 
    if (!currentGroup || currentGroup.date !== d) { 
      currentGroup = { date: d, formatted: formatMoisAnnee(d), plantes: [] }; 
      groupes.push(currentGroup); 
    } 
    currentGroup.plantes.push(pl); 
  }); 
  return groupes; 
});

function obtenirPlantesUnitaires(parcelle) { const plantes = []; const saison = saisonActive.value === 'ete' ? 'plantations_ete' : 'plantations_hiver'; if (!parcelle[saison]) return plantes; parcelle[saison].forEach(pl => { for (let i = 0; i < pl.quantite; i++) { plantes.push({ nom: pl.nom, icone: pl.icone || '🌱' }) } }); return plantes; }
function calculerGrillePlantes(parcelle) { const totalPlants = obtenirPlantesUnitaires(parcelle).length; if (totalPlants === 0) return { display: 'none' }; const colonnes = Math.ceil(Math.sqrt(totalPlants)); const lignes = Math.ceil(totalPlants / colonnes); return { display: 'grid', gridTemplateColumns: `repeat(${colonnes}, 1fr)`, gridTemplateRows: `repeat(${lignes}, 1fr)`, width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, padding: '8px', alignItems: 'center', justifyItems: 'center', pointerEvents: 'none' }; }

const culturesPlantees = computed(() => { const recap = {}; (parcelles.value || []).forEach(p => { const saison = saisonActive.value === 'ete' ? 'plantations_ete' : 'plantations_hiver'; if ((!p.type || p.type === 'bac') && p[saison]) { p[saison].forEach(pl => { if (!recap[pl.id_graine]) { recap[pl.id_graine] = { id: pl.id_graine, nom: pl.nom, icone: pl.icone, quantiteTotale: 0, type: 'Inconnu' } }; recap[pl.id_graine].quantiteTotale += pl.quantite; }); } }); return Object.values(recap).sort((a, b) => b.quantiteTotale - a.quantiteTotale); });

const totalPlantsCultives = computed(() => culturesPlantees.value.reduce((acc, c) => acc + c.quantiteTotale, 0));
const bacsTotal = computed(() => (parcelles.value || []).filter(p => !p.type || p.type === 'bac').length);
const bacsUtilises = computed(() => (parcelles.value || []).filter(p => { const saison = saisonActive.value === 'ete' ? 'plantations_ete' : 'plantations_hiver'; return (!p.type || p.type === 'bac') && p[saison] && p[saison].length > 0; }).length);

</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Inter:wght@300;400;500;600;700&display=swap');
:root { --bg-app: #f4f6f5; --bg-sidebar: #131b16; --accent-gold: #d4af37; --text-main: #2c3e35; --text-muted: #758a7e; --border-light: #e0e5e2; --wood-border: #5d4037; --soil-bg: #3e2723; --grass-bg: #4a6b44; }
body { margin: 0; font-family: 'Inter', sans-serif; background-color: var(--bg-app); color: var(--text-main); overflow: hidden; -webkit-font-smoothing: antialiased;}
.layout { display: flex; height: 100vh; width: 100vw; position: relative; }
.content { flex-grow: 1; display: flex; flex-direction: column; height: 100vh; transition: width 0.3s; width: 100%;}
.vue-scrollable { overflow-y: auto; padding: 40px; height: 100%; background: white; box-sizing: border-box;}

/* MOBILE ELEMENTS */
.btn-hamburger { display: none; position: fixed; top: 15px; left: 15px; z-index: 900; background: white; border: 1px solid var(--border-light); border-radius: 8px; font-size: 24px; padding: 5px 12px; cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,0.1); color: var(--text-main);}
.show-on-mobile { display: none; }

/* --- SIDEBAR --- */
.sidebar { width: 280px; background: var(--bg-sidebar); color: white; padding: 30px 20px; flex-shrink: 0; z-index: 2000; display: flex; flex-direction: column; position: relative; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);}
.sidebar.reduit { width: 80px; padding: 30px 10px; align-items: center;}
.btn-toggle-menu { position: absolute; top: 35px; right: -14px; width: 28px; height: 28px; border-radius: 50%; background: white; border: 1px solid var(--border-light); color: var(--text-main); font-size: 18px; line-height: 1; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); z-index: 30;}
.btn-close-mobile { display: none; position: absolute; top: 15px; right: 15px; background: transparent; border: none; color: white; font-size: 30px; cursor: pointer; }
.logo-container { display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 40px; transition: all 0.3s; }
.logo-img { width: 150px; height: auto; transition: all 0.3s; opacity: 0.9; }
.sidebar.reduit .logo-container .logo-img { width: 50px; }
.titre-sensuel { font-family: 'Cinzel Decorative', serif; font-size: 1.4em; margin: 0; text-align: center; color: var(--accent-gold); font-weight: 700; letter-spacing: 1.5px; line-height: 1.3;}
.sidebar ul { list-style: none; padding: 0; margin: 0; flex-grow: 1; width: 100%;}
.sidebar li { position: relative; padding: 12px 16px; cursor: pointer; margin-bottom: 8px; border-radius: 6px; font-weight: 400; font-size: 0.95em; color: rgba(255,255,255,0.6); display: flex; align-items: center; gap: 12px; transition: all 0.2s; border: 1px solid transparent; position: relative;}
.sidebar li .icone { width: 28px; text-align: center; display: inline-block; font-size: 1.2em; opacity: 0.7; }
.sidebar li:hover { color: white; background: rgba(255,255,255,0.03); }
.sidebar li.actif { background: rgba(212, 175, 55, 0.08); color: var(--accent-gold); border: 1px solid rgba(212, 175, 55, 0.2); font-weight: 500;}
.sidebar li.actif .icone { opacity: 1; }

.badge-notif { background: #f44336; color: white; font-size: 0.7em; padding: 2px 6px; border-radius: 10px; font-weight: bold; margin-left: auto; }
.badge-notif-mini { position: absolute; top: 10px; right: 25px; background: #f44336; width: 8px; height: 8px; border-radius: 50%; }

.menu-bottom-actions { display: flex; flex-direction: column; gap: 10px; margin-top: auto;}
.btn-ajouter-graine { padding: 14px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; background: transparent; color: var(--accent-gold); border: 1px solid var(--accent-gold); border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 0.95em; transition: all 0.2s;}
.btn-ajouter-graine:hover { background: var(--accent-gold); color: var(--bg-sidebar); }

.btn-arroser-tout { padding: 14px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; background: #0288d1; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.95em; transition: background 0.2s; box-shadow: 0 4px 10px rgba(2, 136, 209, 0.4);}
.btn-arroser-tout:hover { background: #0277bd; }

/* --- POTAGER --- */
.vue-potager { position: relative; height: 100%; width: 100%; display: flex; overflow: hidden;}
.workspace-terrain { flex-grow: 1; height: 100%; position: relative; overflow: hidden; background-color: var(--grass-bg); transition: background-color 1s ease; touch-action: none; }
.workspace-terrain.mode-ete { background-color: #5f8d4e; background-image: linear-gradient(115deg, rgba(255,255,255,0.03) 25%, transparent 25%, transparent 75%, rgba(255,255,255,0.03) 75%, rgba(255,255,255,0.03)), linear-gradient(245deg, rgba(0,0,0,0.03) 25%, transparent 25%, transparent 75%, rgba(0,0,0,0.03) 75%, rgba(0,0,0,0.03)); background-size: 20px 20px; }

/* MODIFICATION COULEUR MODE HIVER */
.workspace-terrain.mode-hiver { background-color: #8fa693; }

/* ANIMATION NEIGE GLOBALE */
.workspace-terrain.mode-hiver::before { content: ''; position: absolute; top:0; left:0; width: 100%; height: 100%; pointer-events: none; z-index: 10; background-image: radial-gradient(rgba(255,255,255,0.9) 1px, transparent 2px), radial-gradient(rgba(255,255,255,0.8) 1px, transparent 2px); background-size: 50px 50px, 70px 70px; background-position: 0 0, 25px 25px; animation: neige 20s linear infinite; }
@keyframes neige { from { background-position: 0 0, 25px 25px; } to { background-position: 500px 1000px, 725px 1000px; } }

/* ANIMATION PLUIE GLOBALE */
.pluie-globale-overlay { position: absolute; inset: 0; pointer-events: none; z-index: 99; background: rgba(3, 169, 244, 0.1); background-image: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0.3)); animation: fadeInOut 2.5s ease; }
.pluie-globale-overlay::after { content: '💧 💧 💧 💧 💧 💧 💧 💧 💧 💧 💧 💧 💧 💧'; font-size: 24px; position: absolute; top: -50px; left: 0; width: 100%; display: flex; justify-content: space-around; animation: pluieAnimGlobal 0.4s linear infinite; }
@keyframes pluieAnimGlobal { 0% { transform: translateY(-50px); opacity: 0; } 50% { opacity: 1; } 100% { transform: translateY(100vh); opacity: 0; } }
@keyframes fadeInOut { 0% { opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { opacity: 0; } }

/* --- BARRE D'OUTILS GAUCHE --- */
.toolbar-vertical { position: absolute; top: 20px; left: 20px; display: flex; flex-direction: column; gap: 8px; background: rgba(255,255,255,0.95); backdrop-filter: blur(8px); padding: 10px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.15); z-index: 110; pointer-events: auto; }
.btn-tool-v { width: 44px; height: 44px; border: none; background: transparent; border-radius: 8px; font-size: 1.4em; cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--text-muted); transition: 0.2s; }
.btn-tool-v:hover { background: #f0f4f1; color: var(--text-main); }
.btn-tool-v.actif { background: white; color: var(--text-main); box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 2px solid var(--accent-gold); }
.zoom-text-v { font-size: 0.7em; font-weight: bold; text-align: center; color: var(--text-main); }
.separateur-v { width: 60%; height: 2px; background: var(--border-light); margin: 2px auto; }
.btn-saison-v { font-size: 1.6em; }
.arrosoir-global-btn { color: #0288d1; }

.terrain-infini { position: absolute; width: 10000px; height: 10000px; left: 50%; top: 50%; margin-left: -5000px; margin-top: -5000px; background-image: linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px); background-size: 40px 40px, 40px 40px; cursor: crosshair; transform-origin: center center; z-index: 1;}
.centre-absolu { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.5); font-weight: 500; font-size: 0.8em; pointer-events: none;}

/* ELEMENTS DU TERRAIN UNIFIÉS */
.element-terrain { position: absolute; display: flex; justify-content: center; align-items: center; cursor: grab; transition: border-color 0.5s; box-sizing: border-box; }
.element-terrain.en-mouvement { z-index: 100; cursor: grabbing; box-shadow: 0 15px 30px rgba(0,0,0,0.4), inset 0 2px 5px rgba(0,0,0,0.4); transform: scale(1.01);}
.element-terrain.en-cours-dessin { opacity: 0.7; pointer-events: none; }

/* TYPE: BAC */
.element-terrain.type-bac { border: 10px solid var(--wood-border); border-radius: 4px; box-shadow: 0 5px 10px rgba(0,0,0,0.3), inset 0 2px 5px rgba(0,0,0,0.4); background: var(--wood-border); }
.element-terrain.type-bac.en-cours-dessin { background: transparent; border: 4px dashed var(--wood-border); }
.element-terrain.type-bac.en-cours-dessin .terre-interieure { background-color: rgba(62, 39, 35, 0.3); background-image: none; box-shadow: none;}
.terre-interieure { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--soil-bg); border-radius: 2px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); overflow: hidden; transition: background-color 0.5s; }

/* TYPE: BORDURE (Clôture) */
.element-terrain.type-bordure { height: 12px; background: #8B5A2B; background-image: repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(0,0,0,0.1) 5px, rgba(0,0,0,0.1) 10px); border-radius: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.4); transform-origin: 0 50%; }

/* TYPE: ARBRE & DECO */
.element-terrain.type-arbre, .element-terrain.type-deco { background: transparent; border: 2px dashed transparent; border-radius: 8px; transform: translate(-50%, -50%); width: 60px !important; height: 60px !important;}
.element-terrain.type-arbre:hover, .element-terrain.type-deco:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.8); }
.element-terrain.type-arbre::before { content: '🌳'; display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; filter: drop-shadow(0 10px 10px rgba(0,0,0,0.4)); line-height: 1; }
.element-terrain.type-arbre.taille-Petit { width: 40px !important; height: 40px !important; }
.element-terrain.type-arbre.taille-Petit::before { font-size: 40px; }
.element-terrain.type-arbre.taille-Moyen { width: 80px !important; height: 80px !important; }
.element-terrain.type-arbre.taille-Moyen::before { font-size: 80px; }
.element-terrain.type-arbre.taille-Grand { width: 140px !important; height: 140px !important; }
.element-terrain.type-arbre.taille-Grand::before { font-size: 140px; }

.icone-deco { display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; filter: drop-shadow(0 5px 5px rgba(0,0,0,0.3)); line-height: 1; font-size: 40px;}

.workspace-terrain.mode-hiver .element-terrain.type-bac { border-color: #6a5e5a; }
.workspace-terrain.mode-hiver .element-terrain.type-bac .terre-interieure { background-color: #554d48; }
.workspace-terrain.mode-hiver .element-terrain.type-bordure { background: #6a5e5a; }

.pluie-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(3, 169, 244, 0.2); z-index: 20; pointer-events: none; overflow: hidden; border-radius: 2px;}
.pluie-container::before { content: '💧💧💧💧💧💧'; position: absolute; font-size: 14px; top: -20px; animation: pluieAnim 0.5s linear infinite; display: flex; flex-wrap: wrap; text-align: center; width: 100%; justify-content: space-around;}
@keyframes pluieAnim { 0% { transform: translateY(-10px); opacity: 1; } 100% { transform: translateY(100px); opacity: 0; } }

.indicateur-soif { position: absolute; bottom: 10px; right: 10px; font-size: 24px; animation: clignoteSoif 1.5s infinite; z-index: 15; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); pointer-events: none;}
@keyframes clignoteSoif { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.9); } }

/* BOUTONS ACTIONS FLOTTANTS COMMUNS À TOUS LES ÉLÉMENTS */
.parcelle-actions-container { position: absolute; top: -45px; left: 50%; transform: translateX(-50%); display: none; gap: 6px; background: white; padding: 6px 10px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); z-index: 1000; white-space: nowrap; }
.element-terrain:hover .parcelle-actions-container { display: flex; }
.btn-action-parcelle { width: 32px; height: 32px; border-radius: 50%; border: 2px solid var(--border-light); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; background: white; transition: 0.2s; }
.btn-action-parcelle:hover { border-color: var(--text-main); transform: scale(1.1); }
.btn-supprimer { color: #d32f2f; }
.btn-planter { color: #388e3c; }
.btn-arroser { color: #0288d1; background: #e1f5fe; border-color: #0288d1; } 
.btn-gerer { color: #1976d2; }
.btn-historique { color: #8e24aa; }

.grille-plantes { z-index: 5; } .plante-visuelle { font-size: 1.2em; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.5));}
.label-dim { position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: 0.75em; font-weight: 700; color: #000; pointer-events: none; text-shadow: 1px 1px 2px rgba(255,255,255,0.7), -1px -1px 2px rgba(255,255,255,0.7); white-space: nowrap;}
.label-dim-arbre { position: absolute; bottom: -25px; left: 50%; transform: translateX(-50%); font-size: 0.85em; font-weight: 700; color: #000; pointer-events: none; text-shadow: 1px 1px 2px rgba(255,255,255,0.8); white-space: nowrap; z-index: 30;}

/* POIGNÉE DE REDIMENSIONNEMENT */
.resize-handle { position: absolute; right: -8px; bottom: -8px; width: 16px; height: 16px; background: white; border: 3px solid var(--wood-border); border-radius: 50%; cursor: nwse-resize; z-index: 100;}
.element-terrain.type-bordure .resize-handle { right: -8px; top: -2px; bottom: auto; cursor: crosshair; }

.conflit-actif { animation: pulseRed 3s infinite; }
@keyframes pulseRed { 0% { box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.5); border-color: #d32f2f; } 70% { box-shadow: 0 0 0 10px rgba(211, 47, 47, 0); border-color: var(--wood-border); } 100% { box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); border-color: var(--wood-border); } }
.indicateur-conflit { position: absolute; top: -12px; left: -12px; background: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; border: 2px solid #d32f2f; z-index: 60; box-shadow: 0 2px 5px rgba(0,0,0,0.3); cursor: help;}

/* MODALE DECO (Grille) */
.grille-emojis-deco { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; background: #fafcfa; border: 1px solid var(--border-light); border-radius: 8px; padding: 15px; }
.emoji-deco-item { font-size: 2.5rem; cursor: pointer; padding: 10px; border-radius: 12px; transition: 0.2s; border: 2px solid transparent; }
.emoji-deco-item:hover { background: #e0e5e2; transform: scale(1.1); }
.emoji-deco-item.actif { background: white; border-color: var(--accent-gold); box-shadow: 0 4px 10px rgba(0,0,0,0.1); transform: scale(1.1); }

/* TIMELINE HISTORIQUE (PANNEAU DROIT) */
.panel-historique { width: 320px; background: white; border-left: 1px solid var(--border-light); z-index: 120; display: flex; flex-direction: column; transform: translateX(100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: absolute; right: 0; top: 0; height: 100%; box-shadow: -5px 0 20px rgba(0,0,0,0.05);}
.panel-historique.ouvert { transform: translateX(0); }
.ph-header { padding: 20px; border-bottom: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: center; background: #fafcfa;}
.ph-header h3 { margin: 0; font-family: 'Cinzel Decorative', serif; font-size: 1.2em;}
.btn-fermer-ph { background: transparent; border: none; font-size: 24px; cursor: pointer;}
.ph-content { flex-grow: 1; overflow-y: auto; padding: 20px;}
.timeline { border-left: 2px solid #e0e5e2; margin-left: 10px; padding-left: 20px; position: relative;}
.tl-item { margin-bottom: 25px; position: relative;}
.tl-item::before { content: ''; position: absolute; left: -25px; top: 2px; width: 10px; height: 10px; background: white; border: 2px solid var(--accent-gold); border-radius: 50%;}
.tl-date { font-weight: bold; color: var(--accent-gold); margin-bottom: 10px; text-transform: capitalize;}
.tl-plantes { display: flex; flex-direction: column; gap: 8px;}
.tl-plante { display: flex; align-items: center; gap: 10px; background: #fafcfa; padding: 10px; border-radius: 8px; border: 1px solid var(--border-light);}
.tl-icone { font-size: 1.5em; }
.tl-info { display: flex; flex-direction: column; gap: 4px; }
.tl-nom { font-size: 0.9em; font-weight: 500; color: var(--text-main); }
.badge-saison-petit { font-size: 0.65em; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: inline-block; text-transform: uppercase; align-self: flex-start; color: white;}
.badge-saison-petit.ete { background: #f57f17; }
.badge-saison-petit.hiver { background: #0288d1; }
/* ARCHIVE HISTORIQUE */
.plante-archivee { text-decoration: line-through; opacity: 0.6; }
.badge-saison-petit.archive { background: #9e9e9e; }


/* AUTRES VUES (COMMUNES) */
.header-epure { margin-bottom: 30px; border-bottom: 1px solid var(--border-light); padding-bottom: 20px;}
.header-epure h2 { margin: 0 0 5px 0; font-family: 'Cinzel Decorative', serif; font-size: 2em; color: var(--text-main);}
.sous-titre { margin: 0; color: var(--text-muted); font-size: 1em;}
.section-titre { font-family: 'Cinzel Decorative', serif; color: var(--text-main); font-size: 1.5em; border-bottom: 2px solid var(--border-light); padding-bottom: 10px; margin-bottom: 20px;}
.flex-between { display: flex; justify-content: space-between; align-items: center; }

.info-bulle { display: inline-block; background: #e1f5fe; color: #0277bd; padding: 10px 15px; border-radius: 8px; font-size: 0.85em; border: 1px solid #b3e5fc; line-height: 1.4;}
.info-bulle b { color: #01579b; }

.filtres-bar { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px; background: #fafcfa; padding: 15px; border-radius: 12px; border: 1px solid var(--border-light);}
.search-group { flex: 2; position: relative; display: flex; align-items: center; min-width: 200px;}
.search-icon { position: absolute; left: 12px; opacity: 0.5; font-size: 1.1em; pointer-events: none;}
.search-group input { padding-left: 40px; }
.select-group { flex: 1; display: flex; min-width: 150px;}

.workspace-graines { margin-top: 10px; }
.grid-graines { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }
.carte-graine { background: white; border-radius: 12px; border: 1px solid var(--border-light); box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: all 0.2s; position: relative; overflow: hidden;}
.carte-graine:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); border-color: #cbd4cf;}
.carte-godet { border-left: 4px solid #8d6e63; }
.carte-actions { position: absolute; top: 12px; right: 12px; display: flex; gap: 6px; opacity: 0;}
.carte-graine:hover .carte-actions { opacity: 1; }
.btn-icon { background: white; border: 1px solid var(--border-light); border-radius: 4px; padding: 4px 8px; cursor: pointer; color: var(--text-muted); font-size: 14px;}
.carte-contenu { padding: 24px;}
.carte-top { display: flex; gap: 15px; align-items: flex-start; margin-bottom: 20px;}
.icone-graine { font-size: 2.5em; background: #f4f6f5; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid var(--border-light);}
.titre-graine { display: flex; flex-direction: column; gap: 6px; flex-grow: 1;}
.titre-graine h3 { margin: 0; font-size: 1.2em; color: var(--text-main); font-weight: 600; line-height: 1.2;}

.badge-action-possession { background: #f4f6f5; color: var(--text-muted); border: 1px solid var(--border-light); padding: 4px 8px; border-radius: 6px; font-size: 0.7em; cursor: pointer; font-weight: 600; transition: all 0.2s; font-family: inherit;}
.badge-action-possession.possede { background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7; }
.badge-action-possession:hover { filter: brightness(0.95); }

.badge { align-self: flex-start; background: #f0f4f1; color: var(--text-muted); padding: 4px 10px; border-radius: 4px; font-size: 0.75em; font-weight: 500; border: 1px solid #e0e5e2;}
.badge-godet-actif { background: #efebe9; color: #5d4037; font-size: 0.65em; padding: 2px 6px; border-radius: 4px; border: 1px solid #d7ccc8; font-weight: 600;}
.infos-agronomiques { background: #fafcfa; padding: 15px; border-radius: 8px; border: 1px dashed var(--border-light); display: flex; flex-direction: column; gap: 10px;}
.infos-agronomiques-mini-grid { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 5px; }
.info-tag { background: #e0e5e2; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin: 0; }
.ligne-saison { display: flex; align-items: center; gap: 8px; font-size: 0.85em; color: var(--text-main);}

/* --- CONSEILS ASSOCIATIONS --- */
.carte-conseil { border-left: 4px solid #4caf50; }
.assoc-titre { margin: 0 0 15px 0; color: var(--text-main); font-size: 1.4em; border-bottom: 1px solid var(--border-light); padding-bottom: 10px;}
.assoc-bloc { background: #fafcfa; border-radius: 8px; padding: 15px;}
.assoc-bloc.fav { border: 1px dashed #c8e6c9; }
.assoc-bloc.defav { border: 1px dashed #ffcdd2; }
.assoc-header { font-size: 0.9em; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;}
.assoc-icon { font-size: 1.2em; }
.tags-container { display: flex; flex-wrap: wrap; gap: 8px;}
.tag { font-size: 0.75em; padding: 4px 10px; border-radius: 12px; font-weight: 500; text-transform: capitalize;}
.tag-fav { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9;}
.tag-defav { background: #ffebee; color: #c62828; border: 1px solid #ffcdd2;}
.tag-vide { background: #f5f5f5; color: #9e9e9e; font-style: italic;}

.alerte-assoc { margin-top: 15px; padding: 12px 15px; border-radius: 8px; display: flex; align-items: flex-start; gap: 10px; font-size: 0.9em; line-height: 1.4;}
.box-fav { background: #e8f5e9; border: 1px solid #c8e6c9; color: #2e7d32; }
.box-defav { background: #ffebee; border: 1px solid #ffcdd2; color: #c62828; }

/* --- ROTATION DES CULTURES & TABLEAUX --- */
.rotation-grid { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 20px; position: relative; }
.carte-rotation { flex: 1; min-width: 220px; background: white; border-radius: 12px; border: 1px solid var(--border-light); box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; flex-direction: column; position: relative; }
.rotation-header { padding: 15px; border-top-left-radius: 12px; border-top-right-radius: 12px; color: white; display: flex; flex-direction: column; gap: 5px; }
.rotation-header.legumineuses { background: #66bb6a; }
.rotation-header.feuilles { background: #43a047; }
.rotation-header.racines { background: #795548; }
.rotation-header.fruits { background: #e53935; }
.step-badge { background: rgba(0,0,0,0.2); align-self: flex-start; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
.rotation-header h3 { margin: 0; font-size: 1.1em; }
.carte-contenu-rot { padding: 15px; flex-grow: 1;}
.desc-rotation { font-size: 0.9em; color: var(--text-muted); margin: 0; line-height: 1.4; }
.tag-rotation { background: #f0f4f1; border: 1px solid var(--border-light); color: var(--text-main); }
.arrow-next { position: absolute; right: -18px; top: 50%; transform: translateY(-50%); font-size: 24px; color: var(--border-light); z-index: 10; background: var(--bg-app); border-radius: 50%; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center;}
.show-on-mobile-inline { display: none; }

.table-responsive { overflow-x: auto; }
.table-familles { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid var(--border-light); }
.table-familles th { background: #fafcfa; padding: 15px; text-align: left; color: var(--text-main); font-weight: 600; border-bottom: 1px solid var(--border-light); }
.table-familles td { padding: 15px; border-bottom: 1px solid var(--border-light); font-size: 0.9em; color: var(--text-muted); }
.table-familles tr:last-child td { border-bottom: none; }
.badge-famille { padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 0.9em; color: white; display: inline-block;}
.badge-famille.legumineuses { background: #66bb6a; }
.badge-famille.feuilles { background: #43a047; }
.badge-famille.racines { background: #795548; }
.badge-famille.fruits { background: #e53935; }

.tips-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
.tip-card { background: #fafcfa; border: 1px solid var(--border-light); border-radius: 12px; padding: 20px; display: flex; gap: 15px; align-items: flex-start; }
.tip-icon { font-size: 2em; line-height: 1; }
.tip-content h4 { margin: 0 0 5px 0; color: var(--text-main); font-size: 1.1em; }
.tip-content p { margin: 0; font-size: 0.9em; color: var(--text-muted); line-height: 1.4; }

/* --- ALERTES SAISONS & NOTIFICATIONS --- */
.alertes-grid { display: flex; flex-direction: column; gap: 30px; }
.alertes-container { background: #fff8e1; border: 1px solid #ffecb3; padding: 20px; border-radius: 12px; margin-bottom: 30px;}
.arrosage-container { background: #e1f5fe; border-color: #81d4fa; }
.alertes-container h3 { margin: 0 0 15px 0; font-size: 1.1em; color: #f57f17; display: flex; align-items: center; gap: 8px;}
.arrosage-container h3 { color: #0288d1; }
.liste-alertes { display: flex; flex-direction: column; gap: 10px; }
.alerte-item { display: flex; align-items: center; gap: 12px; padding: 12px 15px; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-left: 4px solid #ccc;}
.alerte-item.godet { border-left-color: #8d6e63; }
.alerte-item.semis { border-left-color: #4caf50; }
.alerte-item.recolte { border-left-color: #ff9800; }
.alerte-item.arrosage { border-left-color: #03a9f4; }
.alerte-icone { font-size: 1.5em; }
.alerte-texte { font-size: 0.9em; color: var(--text-main); flex-grow: 1;}
.alerte-texte b { color: var(--text-main); font-weight: 600; }
.arrosage-sous-texte { display: block; font-size: 0.85em; color: #666; margin-top: 4px; }
.btn-arroser-petit { background: #03a9f4; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.85em; transition: 0.2s;}
.btn-arroser-petit:hover { background: #0288d1; }

.mt-15 { margin-top: 15px; }
.mt-30 { margin-top: 30px; }
.mb-15 { margin-bottom: 15px; }
.mb-30 { margin-bottom: 30px; }

/* STATS ET MÉTÉO */
.meteo-dashboard { display: flex; gap: 20px; background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%); border-radius: 16px; padding: 25px; border: 1px solid #80deea; color: #006064; box-shadow: 0 8px 24px rgba(0,0,0,0.05);}
.meteo-current { flex: 1; display: flex; flex-direction: column; justify-content: center; border-right: 1px solid rgba(0, 151, 167, 0.2); padding-right: 20px;}
.meteo-city { font-weight: 600; font-size: 1.1em; margin-bottom: 10px; opacity: 0.8;}
.meteo-main { display: flex; align-items: center; gap: 15px;}
.meteo-icon-large { font-size: 4em; line-height: 1;}
.meteo-temp-large { font-size: 3.5em; font-weight: 700; font-family: 'Cinzel Decorative', serif;}
.meteo-desc { font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; opacity: 0.8; font-size: 0.9em;}
.meteo-forecast-grid { flex: 2; display: flex; gap: 15px; align-items: center;}
.forecast-card { flex: 1; background: rgba(255,255,255,0.6); backdrop-filter: blur(4px); padding: 15px; border-radius: 12px; display: flex; flex-direction: column; align-items: center; gap: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.02);}
.fc-date { font-weight: 600; text-transform: capitalize; color: #00838f;}
.fc-icon { font-size: 2em; }
.fc-temp { font-weight: 700; color: #006064;}

.meteo-placeholder { width: 100%; background: #fafcfa; border: 2px dashed var(--border-light); padding: 30px; border-radius: 16px; display: flex; align-items: center; gap: 20px; cursor: pointer; color: var(--text-muted); transition: 0.2s;}
.meteo-placeholder:hover { background: white; border-color: var(--accent-gold); color: var(--accent-gold);}
.meteo-placeholder.erreur { border-color: #ffcdd2; color: #d32f2f;}
.meteo-placeholder.erreur:hover { background: #ffebee;}
.placeholder-icon { font-size: 3em; }
.placeholder-texte strong { font-size: 1.1em; display: block; margin-bottom: 5px;}
.placeholder-texte p { margin: 0; font-size: 0.9em; opacity: 0.8;}

.stats-dashboard { display: flex; gap: 20px; margin-bottom: 30px;}
.stat-box { flex: 1; background: #fafcfa; border: 1px solid var(--border-light); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center;}
.stat-valeur { font-size: 2.5em; font-weight: 700; color: var(--accent-gold); font-family: 'Cinzel Decorative', serif; line-height: 1;}
.stat-label { font-size: 0.9em; font-weight: 500; color: var(--text-muted); margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;}
.etat-vide { text-align: center; padding: 60px 20px; background: #fafcfa; border: 1px dashed var(--border-light); border-radius: 12px; color: var(--text-muted);}
.etat-vide-petit { text-align: center; padding: 30px 20px; background: #fafcfa; border: 1px dashed var(--border-light); border-radius: 8px; color: var(--text-muted); font-size: 0.9em;}
.pleine-largeur { grid-column: 1 / -1; }
.icone-graine-petit { font-size: 1.8em; background: #f4f6f5; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; border-radius: 8px; border: 1px solid var(--border-light);}
.bulle-quantite { background: var(--text-main); color: white; padding: 8px 12px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1;}
.godet-bulle { background: #8d6e63; }
.qte-nombre { font-size: 1.4em; font-weight: 700; }
.qte-label { font-size: 0.6em; text-transform: uppercase; opacity: 0.8;}

/* --- RÉGLAGES --- */
.grid-reglages { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.carte-reglage { background: white; border-radius: 12px; border: 1px solid var(--border-light); overflow: hidden;}
.carte-discord { border-top: 4px solid #5865F2; } 
.carte-localisation { border-top: 4px solid #03a9f4; }
.reglage-header { background: #fafcfa; padding: 20px; border-bottom: 1px solid var(--border-light); display: flex; align-items: center; gap: 15px;}
.reglage-icone { font-size: 1.8em; }
.reglage-header h3 { margin: 0; font-size: 1.2em; color: var(--text-main); font-weight: 600;}
.reglage-body { padding: 25px; display: flex; flex-direction: column; gap: 20px;}
.reglage-desc { margin: 0; color: var(--text-muted); font-size: 0.9em; line-height: 1.4;}
.separateur-horizontal { height: 1px; background: var(--border-light); margin: 5px 0;}
.input-action { display: flex; gap: 10px; }
.input-action input { flex-grow: 1; }
.form-group { display: flex; flex-direction: column; }
.form-group label { margin-bottom: 8px; font-weight: 500; font-size: 0.85em; color: var(--text-main);}
input, select { padding: 10px; border: 1px solid var(--border-light); border-radius: 6px; font-family: inherit; font-size: 0.95em; transition: all 0.2s; background: #fafcfa; width: 100%; box-sizing: border-box;}
input:focus, select:focus { border-color: var(--accent-gold); outline: none; background: white; box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);}
.btn-submit { background: var(--text-main); color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;}

/* TOGGLE GENERAL */
.toggle-container { display: flex; align-items: center; gap: 12px; cursor: pointer; user-select: none;}
.toggle-container input { display: none; }
.toggle-slider { width: 40px; height: 22px; background: #ccc; border-radius: 20px; position: relative; transition: 0.3s;}
.toggle-slider::before { content: ""; position: absolute; width: 18px; height: 18px; background: white; border-radius: 50%; top: 2px; left: 2px; transition: 0.3s;}
.toggle-container input:checked + .toggle-slider { background: var(--accent-gold); }
.toggle-container input:checked + .toggle-slider::before { transform: translateX(18px); }
.toggle-label { font-size: 0.9em; color: var(--text-main); font-weight: 500;}

/* MODALES */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(19, 27, 22, 0.4); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 1000;}
.modal { background: white; padding: 35px; border-radius: 12px; width: 420px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); border: 1px solid var(--border-light); max-height: 90vh; overflow-y: auto;}
.modal-large { width: 600px; } 
.modal h3 { font-family: 'Cinzel Decorative', serif; color: var(--text-main); margin: 0 0 5px 0; font-size: 1.5em;}
.modal-desc { color: var(--text-muted); font-size: 0.9em; margin-bottom: 25px;}
.form-row { display: flex; gap: 15px; width: 100%; margin-bottom: 15px;}
.form-group.half { flex: 1; }
.form-group.third { flex: 1; }
.form-group.flex-grow { flex-grow: 1; }
.help-text { font-size: 0.75em; color: #d32f2f; margin-top: 5px; }
.icone-selector-container { width: 180px;}
.icone-selector { display: flex; flex-wrap: wrap; gap: 4px; background: #fafcfa; border: 1px solid var(--border-light); border-radius: 6px; padding: 6px; height: 75px; overflow-y: auto;}
.ico-choix { font-size: 1.2em; cursor: pointer; padding: 2px; border-radius: 4px; transition: all 0.2s; border: 1px solid transparent;}
.ico-choix:hover { background: #e0e5e2;}
.ico-choix.ico-actif { background: white; border-color: var(--accent-gold); box-shadow: 0 2px 4px rgba(0,0,0,0.1); transform: scale(1.1);}
.actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 30px; }
.btn-cancel { background: transparent; color: var(--text-muted); padding: 10px 16px; border: 1px solid var(--border-light); border-radius: 6px; cursor: pointer; font-weight: 500;}
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }

/* MODALE DE CONFIRMATION (NOUVEAU) */
.modal-confirm { text-align: center; width: 350px; padding: 25px; }
.confirm-icon { font-size: 3em; margin-bottom: 10px; line-height: 1; }
.btn-danger { background: #d32f2f; color: white; border: none; }
.btn-danger:hover { background: #b71c1c; }

.liste-gestion-plantes { display: flex; flex-direction: column; gap: 10px; }
.item-gestion { display: flex; justify-content: space-between; align-items: center; background: #fafcfa; border: 1px solid var(--border-light); padding: 10px 15px; border-radius: 8px;}
.item-info { display: flex; align-items: center; gap: 10px; font-weight: 500;}
.item-details-flex { display: flex; flex-direction: column; gap: 4px; }
.item-icone { font-size: 1.5em; }
.item-actions { display: flex; gap: 10px; align-items: center;}
input[type="number"].input-qte-petit { width: 60px; padding: 6px; text-align: center;}
input[type="month"].input-date-petit { width: auto; padding: 6px; font-size: 0.85em; color: var(--text-muted); cursor: pointer;}


/* ==========================================
   MEDIA QUERIES (MOBILE RESPONSIVE)
   ========================================== */
@media (max-width: 768px) {
  .layout { flex-direction: column; }
  .btn-hamburger { display: block; }
  .sidebar { position: fixed; top: 0; left: -100%; height: 100vh; width: 280px; box-shadow: 5px 0 15px rgba(0,0,0,0.5); overflow-y: auto; }
  .sidebar.mobile-open { left: 0; }
  .btn-close-mobile { display: block; }
  .mobile-overlay { display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1999; }
  .hide-on-mobile { display: none; }
  .hide-on-mobile-small { display: none !important; }

  .vue-scrollable { padding: 80px 15px 20px 15px; } 
  .grid-reglages { grid-template-columns: 1fr; }
  .block-mobile { display: flex; flex-direction: column; gap: 15px; align-items: flex-start !important; }
  .full-width { width: 100% !important; }
  .mt-mobile { margin-top: 10px; }
  .block-mobile-small { flex-direction: column; align-items: flex-start; gap: 10px; }

  .stats-dashboard { flex-direction: column; }

  .toolbar-vertical { top: 70px; left: 10px; right: 10px; flex-direction: row; flex-wrap: wrap; justify-content: center; width: auto; padding: 6px; gap: 4px; }
  .btn-tool-v { width: 38px; height: 38px; font-size: 1.2em; }
  .separateur-v { width: 2px; height: 24px; margin: auto 4px; }

  .carte-actions { opacity: 1; }
  .flex-col-mobile { flex-direction: column; width: 100%; }
  .full-width-mobile { width: 100%; }

  .modal { padding: 20px; width: 95%; max-width: 400px; }
  .form-row { flex-direction: column; gap: 10px; }
  
  .panel-historique { width: 100%; }
  
  /* ROTATION MOBILE */
  .rotation-grid { flex-direction: column; }
  .arrow-next.hide-on-mobile { display: none; }
  .arrow-next.show-on-mobile-inline { display: flex; position: static; transform: none; margin: -10px auto; z-index: 10; background: transparent; }
  .table-familles th, .table-familles td { padding: 10px; font-size: 0.8em; }
}
</style>