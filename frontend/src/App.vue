<template>
  <div class="layout">
    <div v-if="needsLogin" class="login-screen">
      <form class="modal login-card" @submit.prevent="login">
        <div class="login-language">
          <button v-for="l in LOCALES" :key="l" type="button" :class="['lang-option', { active: locale === l }]" @click="setLocale(l)">{{ l.toUpperCase() }}</button>
        </div>
        <img :src="logoImg" alt="My Secret Garden" class="login-logo" />
        <h3>My Secret Garden</h3>
        <p class="modal-desc">{{ t('login.subtitle') }}</p>
        <div class="form-group">
          <label>{{ t('login.username') }}</label>
          <input type="text" v-model="loginForm.username" autocomplete="username" autofocus />
        </div>
        <div class="form-group mt-15">
          <label>{{ t('login.password') }}</label>
          <input type="password" v-model="loginForm.password" autocomplete="current-password" />
        </div>
        <div v-if="loginError" class="help-text">{{ loginError }}</div>
        <button type="submit" class="btn-submit mt-15" style="width: 100%;" :disabled="!loginForm.username || !loginForm.password || loggingIn">{{ loggingIn ? t('login.signing_in') : t('login.sign_in') }}</button>
      </form>
    </div>

    <nav :class="['sidebar', { collapsed: menuCollapsed, 'mobile-open': mobileMenuOpen }]">
      <button class="btn-toggle-menu hide-on-mobile" @click="menuCollapsed = !menuCollapsed" :title="menuCollapsed ? t('nav.expand') : t('nav.collapse')"><Icon :name="menuCollapsed ? 'expand' : 'collapse'" :size="18" /></button>
      <button class="btn-close-mobile" @click="mobileMenuOpen = false" :title="t('nav.close')"><Icon name="close" :size="18" /></button>

      <div class="logo-container">
        <img :src="logoImg" alt="My Secret Garden" class="logo-img" />
        <h1 v-if="!menuCollapsed" class="brand-title">My Secret Garden</h1>
      </div>

      <ul>
        <li v-for="item in NAV" :key="item.view" :class="{ active: activeView === item.view }" @click="showView(item.view)" :title="t(`nav.${item.view}`)">
          <span class="icon"><Icon :name="item.icon" /></span> <span class="menu-text" v-if="!menuCollapsed">{{ t(`nav.${item.view}`) }}</span>
          <template v-if="item.view === 'notifications' && alertCount > 0">
            <span v-if="!menuCollapsed" class="badge-notif">{{ alertCount }}</span>
            <span v-else class="badge-notif-mini"></span>
          </template>
        </li>
      </ul>

      <div class="sidebar-actions">
        <div v-if="frostDate" class="frost-alert" :title="menuCollapsed ? t('nav.frost_on', { date: frostDate }) : ''">
          <span class="frost-icon"><Icon name="frost" :size="16" /></span>
          <span v-if="!menuCollapsed">{{ t('nav.frost_on', { date: frostDate }) }}</span>
        </div>
        <button v-if="thirstyCount > 0" class="btn-water-all" @click="waterEverything()" :title="t('nav.water_all_title')">
          <span class="icon"><Icon name="water" :size="18" /></span> <span v-if="!menuCollapsed">{{ t('nav.water_all', { n: thirstyCount }) }}</span>
        </button>
        <button class="btn-add-plant" @click="openSeedModal()" :title="t('seeds.new')">
          <span class="icon"><Icon name="plus" :size="18" /></span> <span v-if="!menuCollapsed">{{ t('seeds.new') }}</span>
        </button>
      </div>
    </nav>

    <button class="btn-hamburger" @click="mobileMenuOpen = true" :title="t('nav.open')"><Icon name="menu" /></button>
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false"></div>

    <main class="content">
      <div v-if="defaultCredentials && !needsLogin" class="security-banner">
        ⚠️ <span v-html="t('security.default_credentials_html')"></span>
      </div>

      <!-- GARDEN PLAN -->
      <div v-if="activeView === 'garden'" class="view-garden">
        <div class="workspace canvas-grass" @mousedown="startAction" @mousemove="moveAction" @mouseup="endAction" @mouseleave="endAction" @touchstart.passive="startAction" @touchmove.passive="moveAction" @touchend="endAction" @wheel.prevent="onWheel">
          <div v-if="globalRain" class="global-rain-overlay"></div>

          <div class="toolbar">
            <button :class="['tool-btn', { active: activeTool === 'hand' }]" @click="activeTool = 'hand'" :title="t('garden.tools.hand')"><Icon name="hand" /></button>
            <div class="tool-divider"></div>
            <button :class="['tool-btn', { active: activeTool === 'bed' }]" @click="activeTool = 'bed'" :title="t('garden.tools.bed')"><Icon name="bed" /></button>
            <button :class="['tool-btn', { active: activeTool === 'border' }]" @click="activeTool = 'border'" :title="t('garden.tools.border')"><Icon name="fence" /></button>
            <button :class="['tool-btn', { active: activeTool === 'tree' }]" @click="activeTool = 'tree'" :title="t('garden.tools.tree')"><Icon name="tree" /></button>
            <button :class="['tool-btn', { active: activeTool === 'decor' }]" @click="activeTool = 'decor'" :title="t('garden.tools.decor')"><Icon name="sparkle" /></button>
            <div class="tool-divider"></div>
            <button class="tool-btn water-all-tool" @click="waterEverything" :title="t('garden.tools.water_all')"><Icon name="water" /></button>
            <div class="tool-divider hide-on-mobile-small"></div>
            <button class="tool-btn hide-on-mobile-small" @click="zoomBy(0.1)" :title="t('garden.tools.zoom_in')"><Icon name="plus" /></button>
            <span class="zoom-label hide-on-mobile-small">{{ Math.round(zoom * 100) }}%</span>
            <button class="tool-btn hide-on-mobile-small" @click="zoomBy(-0.1)" :title="t('garden.tools.zoom_out')"><Icon name="minus" /></button>
            <button class="tool-btn hide-on-mobile-small" @click="recenter" :title="t('garden.tools.recenter')"><Icon name="target" /></button>
          </div>

          <div ref="canvasRef" class="canvas" :style="{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }">
            <div class="origin-marker">{{ t('garden.origin') }}</div>

            <div v-for="p in plots" :key="p.id"
                 :class="['plot', `type-${p.type}`, `size-${p.size || 'medium'}`, { dragging: draggedPlot && draggedPlot.id === p.id, 'has-conflict': hasConflict(p) }]"
                 :style="plotStyle(p)"
                 @mousedown.stop="startDrag($event, p)" @touchstart.stop="startDrag($event, p)">

              <template v-if="p.type === 'bed'">
                <div v-if="p._watering" class="rain-overlay"></div>
                <div class="soil">
                  <div class="plant-grid" :style="plantGridStyle(p)">
                    <div v-for="(plant, index) in plantDots(p)" :key="index" class="plant-dot" :title="plant.name">{{ plant.icon }}</div>
                  </div>
                </div>
                <span class="plot-label"><strong v-if="p.name">{{ p.name }} • </strong>{{ p.size_x_cm }} × {{ p.size_y_cm }} cm</span>
                <div v-if="hasConflict(p)" class="conflict-badge" :title="t('garden.conflict')">⚠️</div>
                <div v-if="bedNeedsWater(p) && !p._watering" class="thirst-badge" :title="t('garden.thirsty')">💧</div>
                <div class="resize-handle" @mousedown.stop="startResize($event, p)" @touchstart.stop="startResize($event, p)"></div>
              </template>

              <template v-else-if="p.type === 'decor'">
                <span class="decor-icon">{{ p.icon }}</span>
              </template>

              <template v-else-if="p.type === 'border'">
                <div class="resize-handle" @mousedown.stop="startResize($event, p)" @touchstart.stop="startResize($event, p)"></div>
              </template>

              <div class="plot-actions" :style="actionsStyle(p)">
                <template v-if="p.type === 'bed'">
                  <button class="plot-action btn-water" @click.stop="waterBed(p)" :title="t('garden.actions.water')">💦</button>
                  <button class="plot-action btn-plant" @click.stop="openPlantingModal(p)" :title="t('garden.actions.plant')">🌱</button>
                  <button class="plot-action btn-manage" @click.stop="openManageBed(p)" :title="t('garden.actions.manage')">📋</button>
                  <button class="plot-action btn-history" @click.stop="openHistory(p)" :title="t('garden.actions.history')">🕒</button>
                </template>
                <button class="plot-action btn-delete" @click.stop="deletePlot(p.id)" :title="t('common.delete')">×</button>
              </div>
            </div>

            <div v-if="drawingPlot" :class="['plot', 'drawing', `type-${drawingPlot.type}`]" :style="plotStyle(drawingPlot)">
              <template v-if="drawingPlot.type === 'bed'">
                <div class="soil"></div>
                <span class="plot-label">{{ drawingPlot.size_x_cm }} × {{ drawingPlot.size_y_cm }} cm</span>
              </template>
            </div>
          </div>
        </div>

        <aside :class="['history-panel', { open: historyPlot }]">
          <div class="panel-header">
            <h3>{{ t('garden.history.title') }}</h3>
            <button class="btn-close-panel" @click="closeHistory">×</button>
          </div>
          <div class="panel-body">
            <div v-if="historyGroups.length === 0" class="empty-state-small">{{ t('garden.history.empty') }}</div>
            <div class="timeline" v-else>
              <div v-for="group in historyGroups" :key="group.date" class="tl-item">
                <div class="tl-date">{{ group.label }}</div>
                <div class="tl-plants">
                  <div v-for="(pl, i) in group.plants" :key="i" class="tl-plant">
                    <span class="tl-icon" :style="pl.active ? '' : 'opacity:0.5; filter:grayscale(1);'">{{ pl.icon }}</span>
                    <div class="tl-info">
                      <span :class="['tl-name', { 'plant-archived': !pl.active }]">{{ pl.name }} <b>(x{{ pl.quantity }})</b></span>
                      <div v-if="!pl.active" style="display:flex; gap: 6px; margin-top: 4px;">
                        <span class="badge-small archive" :title="t('garden.history.removed_on', { date: formatMonthYear(pl.removed_on) })">{{ t('garden.history.harvested') }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <!-- SEED LIBRARY -->
      <div v-if="activeView === 'seeds'" class="view-scroll">
        <header class="page-header flex-between block-mobile">
          <div>
            <h2>{{ t('seeds.title') }}</h2>
            <p class="subtitle">{{ t('seeds.subtitle') }}</p>
            <div class="mt-15">
              <span class="tip-box" v-html="t('seeds.tip_html')"></span>
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:10px; width: 220px;" class="full-width mt-mobile">
            <button class="btn-submit full-width" @click="openSeedModal()">+ {{ t('seeds.new') }}</button>
            <div style="display:flex; gap:10px;">
              <button class="btn-cancel" style="flex:1; padding: 8px; font-size: 0.85em;" @click="exportSeeds" :title="t('seeds.export_title')">📤 {{ t('common.export') }}</button>
              <button class="btn-cancel" style="flex:1; padding: 8px; font-size: 0.85em;" @click="$refs.seedImportInput.click()" :title="t('seeds.import_title')">📥 {{ t('common.import') }}</button>
              <input type="file" ref="seedImportInput" @change="onSeedFileSelected" accept=".json" style="display: none;" />
            </div>
          </div>
        </header>

        <div class="section-block">
          <div class="filter-bar block-mobile">
            <div class="form-group search-group full-width">
              <span class="search-icon"><Icon name="search" :size="18" /></span>
              <input type="text" v-model="seedSearch" :placeholder="t('seeds.search')" />
            </div>
            <div class="form-group select-group full-width">
              <select v-model="seedCategoryFilter">
                <option value="">{{ t('seeds.all_categories') }}</option>
                <option v-for="c in CATEGORIES" :key="c" :value="c">{{ t(`category.${c}`) }}</option>
              </select>
            </div>
            <div class="form-group select-group full-width mt-mobile">
              <select v-model="seedStockFilter">
                <option value="all">{{ t('seeds.all_states') }}</option>
                <option value="in_stock">📦 {{ t('seeds.in_stock') }}</option>
                <option value="to_buy">🛒 {{ t('seeds.to_buy') }}</option>
              </select>
            </div>
          </div>

          <div class="card-grid">
            <div v-for="seed in filteredSeeds" :key="seed.id" :class="['card', { 'is-expired': isExpired(seed.expiry) }]">
              <div class="card-actions">
                <button class="btn-icon" @click="openSeedModal(seed)" :title="t('common.edit')">✎</button>
                <button class="btn-icon danger" @click="deleteSeed(seed.id)" :title="t('common.delete')">×</button>
              </div>
              <div class="card-body">
                <div class="card-top">
                  <div class="card-icon">{{ seed.icon }}</div>
                  <div class="card-title">
                    <div class="title-with-badge block-mobile-small">
                      <h3>{{ seed.name }}</h3>
                      <div style="display:flex; gap:8px;">
                        <button :class="['stock-toggle', { 'in-stock': seed.in_stock }]" @click.stop="seed.in_stock = !seed.in_stock">
                          {{ seed.in_stock ? '📦 ' + t('seeds.in_stock') : '🛒 ' + t('seeds.to_buy') }}
                        </button>
                        <span v-if="isInTray(seed.id)" class="badge-in-tray">🌱 {{ t('seeds.in_tray') }}</span>
                      </div>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
                      <span class="badge">{{ categoryLabel(seed.category) }}</span>
                      <span :class="['badge', seed.is_plant ? 'badge-plant' : 'badge-seed']">{{ seed.is_plant ? '🌿 ' + t('seeds.plant') : '🌰 ' + t('seeds.seed') }}</span>
                      <span v-if="isExpired(seed.expiry)" class="badge badge-expired">⚠️ {{ t('seeds.expired') }}</span>
                      <span v-else-if="seed.expiry" class="badge badge-date">⏳ {{ t('seeds.expires', { date: formatMonthYear(seed.expiry) }) }}</span>
                    </div>
                  </div>
                </div>
                <div class="plant-info">
                  <div class="plant-info-tags">
                    <p v-if="seed.soil" class="info-tag"><strong>{{ label('seeds.soil') }}</strong> {{ t(`soil.${seed.soil}`) }}</p>
                    <p v-if="seed.watering_interval" class="info-tag"><strong>{{ label('seeds.water') }}</strong> {{ wateringLabel(seed.watering_interval) }}</p>
                  </div>
                  <div class="info-line" v-if="seed.tray_start && seed.tray_end"><span class="info-icon">🌱</span><span>{{ t('seeds.tray_period', { from: shortMonth(seed.tray_start), to: shortMonth(seed.tray_end) }) }}</span></div>
                  <div class="info-line" v-if="seed.planting_start && seed.planting_end"><span class="info-icon">🌿</span><span>{{ t('seeds.planting_period', { from: shortMonth(seed.planting_start), to: shortMonth(seed.planting_end) }) }}</span></div>
                  <div class="info-line" v-if="seed.harvest_start && seed.harvest_end"><span class="info-icon">🧺</span><span>{{ t('seeds.harvest_period', { from: shortMonth(seed.harvest_start), to: shortMonth(seed.harvest_end) }) }}</span></div>
                </div>
              </div>
            </div>

            <div v-if="filteredSeeds.length === 0" class="empty-state full-row">
              <div class="empty-state-icon">🔍</div>
              <h3>{{ t('seeds.no_match') }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- SEEDLINGS -->
      <div v-if="activeView === 'seedlings'" class="view-scroll">
        <header class="page-header flex-between block-mobile">
          <div>
            <h2>{{ t('seedlings.title') }}</h2>
            <p class="subtitle">{{ t('seedlings.subtitle') }}</p>
          </div>
          <button class="btn-submit full-width mt-mobile" @click="openSeedlingModal()">+ {{ t('seedlings.new') }}</button>
        </header>

        <div class="section-block">
          <div v-if="seedlingCards.length === 0" class="empty-state">
            <div class="empty-state-icon">🌱</div>
            <h3>{{ t('seedlings.empty') }}</h3>
          </div>
          <div class="card-grid" v-else>
            <div v-for="s in seedlingCards" :key="s.id" class="card card-seedling">
              <div class="card-actions">
                <button class="btn-icon" @click="openSeedlingModal(s)" :title="t('common.edit')">✎</button>
                <button class="btn-icon danger" @click="deleteSeedling(s.id)" :title="t('seedlings.done')">✔</button>
              </div>
              <div class="card-body">
                <div class="card-top align-center">
                  <div class="card-icon">{{ s.icon }}</div>
                  <div class="card-title flex-grow">
                    <h3>{{ s.name }}</h3>
                    <span class="badge">{{ categoryLabel(s.category) }}</span>
                  </div>
                  <div class="quantity-bubble tray-bubble">
                    <span class="qty-value">{{ s.quantity }}</span>
                    <span class="qty-label">{{ t('seedlings.trays') }}</span>
                  </div>
                </div>
                <div class="plant-info mt-15" v-if="s.location">
                  <div class="info-line"><span class="info-icon">📍</span><span><strong>{{ label('common.location') }}</strong> {{ s.location }}</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- POTS -->
      <div v-if="activeView === 'pots'" class="view-scroll">
        <header class="page-header flex-between block-mobile">
          <div>
            <h2>{{ t('pots.title') }}</h2>
            <p class="subtitle">{{ t('pots.subtitle') }}</p>
          </div>
          <button class="btn-submit full-width mt-mobile" @click="openPotModal()">+ {{ t('pots.new') }}</button>
        </header>

        <div class="section-block">
          <div class="filter-bar block-mobile" v-if="pots.length > 0">
            <div class="form-group search-group full-width">
              <span class="search-icon"><Icon name="search" :size="18" /></span>
              <input type="text" v-model="potSearch" :placeholder="t('pots.search')" />
            </div>
          </div>

          <div v-if="pots.length === 0" class="empty-state">
            <div class="empty-state-icon">🪴</div>
            <h3>{{ t('pots.empty') }}</h3>
          </div>
          <div v-else-if="potGroups.every(g => g.pots.length === 0)" class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <h3>{{ t('pots.no_match') }}</h3>
          </div>

          <template v-for="group in potGroups" :key="group.environment">
            <div v-if="group.pots.length > 0">
              <h3 class="section-title mt-15">{{ group.environment === 'indoor' ? '🏠 ' + t('pots.indoor_plants') : '☀️ ' + t('pots.outdoor_plants') }}</h3>
              <div class="card-grid mb-30">
                <div v-for="pot in group.pots" :key="pot.id" :class="['card', group.environment === 'indoor' ? 'card-pot' : 'card-pot-outdoor']">
                  <div class="card-actions">
                    <button class="btn-icon" @click="openPotModal(pot)" :title="t('common.edit')">✎</button>
                    <button class="btn-icon danger" @click="deletePot(pot.id)" :title="t('common.delete')">×</button>
                  </div>
                  <div class="card-body">
                    <div class="card-top align-center">
                      <div class="card-icon">{{ pot.icon }}</div>
                      <div class="card-title flex-grow">
                        <h3>{{ pot.name }}</h3>
                        <span :class="['badge', group.environment === 'indoor' ? 'badge-indoor' : 'badge-outdoor']">{{ group.environment === 'indoor' ? '🏠 ' + t('pots.indoor') : '☀️ ' + t('pots.outdoor') }}</span>
                      </div>
                    </div>
                    <div class="plant-info mt-15">
                      <div class="info-line" v-if="pot.location"><span class="info-icon">📍</span><span><strong>{{ label('common.location') }}</strong> {{ pot.location }}</span></div>
                      <div class="info-line"><span class="info-icon">💦</span><span><strong>{{ label('seeds.water') }}</strong> {{ wateringLabel(pot.watering_interval) }}</span></div>
                      <div class="pot-status">
                        <div v-if="potNeedsWater(pot) && !pot._watering" class="badge badge-expired">⚠️ {{ t('pots.thirsty') }}</div>
                        <div v-else-if="pot._watering" class="status-watering">{{ t('pots.watering') }} 💧</div>
                        <div v-else class="status-ok">{{ t('pots.hydrated') }} ✓</div>
                        <button class="btn-water-small" @click="waterPot(pot)">💦 {{ t('pots.water') }}</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- COMPANION PLANTING -->
      <div v-if="activeView === 'companions'" class="view-scroll">
        <header class="page-header">
          <h2>{{ t('companions.title') }}</h2>
          <p class="subtitle">{{ t('companions.subtitle') }}</p>
        </header>

        <div class="section-block">
          <div class="filter-bar">
            <div class="form-group search-group full-width">
              <span class="search-icon"><Icon name="search" :size="18" /></span>
              <input type="text" v-model="companionSearch" :placeholder="t('companions.search')" />
            </div>
          </div>

          <div class="card-grid">
            <div v-for="entry in filteredCompanions" :key="entry.plant" class="card">
              <div class="card-body">
                <h3 class="companion-title">{{ plantName(entry.plant, locale) }}</h3>
                <div class="companion-block good">
                  <div class="companion-header"><span class="companion-icon">✨</span><strong>{{ t('companions.good') }}</strong></div>
                  <div class="tags-container">
                    <span v-for="p in entry.good" :key="'g' + p" class="tag tag-good">{{ plantName(p, locale) }}</span>
                  </div>
                </div>
                <div class="companion-block bad mt-15">
                  <div class="companion-header"><span class="companion-icon">⚠️</span><strong>{{ t('companions.bad') }}</strong></div>
                  <div class="tags-container">
                    <span v-for="p in entry.bad" :key="'b' + p" class="tag tag-bad">{{ plantName(p, locale) }}</span>
                    <span v-if="entry.bad.length === 0" class="tag tag-empty">{{ t('companions.none') }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="filteredCompanions.length === 0" class="empty-state full-row">
              <div class="empty-state-icon">🌱</div><h3>{{ t('companions.no_match') }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- CROP ROTATION -->
      <div v-if="activeView === 'rotation'" class="view-scroll">
        <header class="page-header">
          <h2>{{ t('rotation.title') }}</h2>
          <p class="subtitle">{{ t('rotation.subtitle') }}</p>
        </header>

        <div class="tip-box mb-30" style="display:block;" v-html="t('rotation.how_html')"></div>

        <div class="rotation-grid">
          <div v-for="(group, index) in ROTATION" :key="group.id" class="rotation-card">
            <div class="rotation-header" :class="group.id">
              <span class="step-badge">{{ t('rotation.year', { n: index + 1 }) }}</span>
              <h3>{{ t(`rotation.groups.${group.id}.name`) }}</h3>
            </div>
            <div class="rotation-body">
              <p class="rotation-desc">{{ t(`rotation.groups.${group.id}.desc`) }}</p>
              <div class="tags-container mt-15">
                <span v-for="p in group.plants" :key="p" class="tag tag-rotation">{{ plantName(p, locale) }}</span>
              </div>
            </div>
            <div v-if="index < 3" class="arrow-next hide-on-mobile">➔</div>
            <div v-if="index < 3" class="arrow-next show-on-mobile-inline">⬇</div>
          </div>
        </div>

        <div class="mt-30">
          <h3 class="section-title">{{ t('rotation.table_title') }}</h3>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>{{ t('rotation.columns.category') }}</th>
                  <th>{{ t('rotation.columns.plants') }}</th>
                  <th>{{ t('rotation.columns.planting') }}</th>
                  <th>{{ t('rotation.columns.season') }}</th>
                  <th>{{ t('rotation.columns.exposure') }}</th>
                  <th>{{ t('rotation.columns.watering') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in FAMILY_NEEDS" :key="row.id">
                  <td><span :class="['badge-family', row.family]">{{ t(`reference.needs.${row.id}.label`) }}</span></td>
                  <td><strong>{{ t(`reference.needs.${row.id}.plants`) }}</strong></td>
                  <td>{{ t(`reference.needs.${row.id}.planting`) }}</td>
                  <td>{{ t(`reference.needs.${row.id}.season`) }}</td>
                  <td>{{ t(`reference.needs.${row.id}.sun`) }}</td>
                  <td>{{ t(`reference.needs.${row.id}.water`) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="mt-30">
          <h3 class="section-title">{{ t('rotation.soil_title') }}</h3>
          <div class="tips-grid">
            <div v-for="tip in SOIL_TIPS" :key="tip.id" class="tip-card">
              <div class="tip-icon">{{ tip.icon }}</div>
              <div class="tip-content">
                <h4>{{ t(`reference.soil_tips.${tip.id}.title`) }}</h4>
                <p>{{ t(`reference.soil_tips.${tip.id}.text`) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- NOTIFICATIONS -->
      <div v-if="activeView === 'notifications'" class="view-scroll">
        <header class="page-header flex-between block-mobile">
          <div>
            <h2>{{ t('notifications.title') }}</h2>
            <p class="subtitle">{{ t('notifications.subtitle') }}</p>
          </div>
          <button v-if="thirstyCount > 0" class="btn-water-small full-width mt-mobile" @click="waterEverything()">💦 {{ t('notifications.water_all') }}</button>
        </header>

        <div v-if="alertCount === 0" class="empty-state">
          <div class="empty-state-icon">✨</div>
          <h3>{{ t('notifications.all_clear') }}</h3>
        </div>

        <div class="alert-groups" v-else>
          <div class="alert-group watering-group" v-if="bedAlerts.length > 0">
            <h3><span class="heading-icon">💧</span> {{ t('notifications.beds_title') }}</h3>
            <div class="alert-list">
              <div v-for="alert in bedAlerts" :key="'bed' + alert.bed.id" class="alert-item watering block-mobile">
                <div class="alert-icon hide-on-mobile-small">💦</div>
                <div class="alert-text">
                  <span v-html="t('notifications.bed_thirsty_html', { name: escapeHtml(alert.bed.name || t('notifications.unnamed_bed')) })"></span>
                  <span class="alert-subtext">{{ t('notifications.last_watered', { n: alert.days }) }}</span>
                </div>
                <button class="btn-water-small full-width" @click="waterBed(alert.bed); goToBed(alert.bed)">{{ t('notifications.watered') }}</button>
              </div>
            </div>
          </div>

          <div class="alert-group watering-group" v-if="potAlerts.length > 0">
            <h3><span class="heading-icon">🪴</span> {{ t('notifications.pots_title') }}</h3>
            <div class="alert-list">
              <div v-for="alert in potAlerts" :key="'pot' + alert.pot.id" class="alert-item watering alert-pot block-mobile">
                <div class="alert-icon hide-on-mobile-small">{{ alert.pot.icon }}</div>
                <div class="alert-text">
                  <span v-html="t('notifications.pot_thirsty_html', { name: escapeHtml(alert.pot.name), place: escapeHtml(alert.place) })"></span>
                  <span class="alert-subtext">{{ t('notifications.last_watered', { n: alert.days }) }}</span>
                </div>
                <button class="btn-water-small btn-water-pot full-width" @click="waterPot(alert.pot)">{{ t('notifications.watered') }}</button>
              </div>
            </div>
          </div>

          <div class="alert-group" v-if="calendarAlerts.length > 0">
            <h3><span class="heading-icon">📅</span> {{ t('notifications.calendar_title') }}</h3>
            <div class="alert-list">
              <div v-for="(alert, i) in calendarAlerts" :key="i" :class="['alert-item', alert.type]">
                <div class="alert-icon">{{ alert.icon }}</div>
                <div class="alert-text">
                  <strong>{{ t('common.label', { text: alert.distance === 0 ? t('notifications.this_month') : t('notifications.in_months', { n: alert.distance }) }) }}</strong>
                  {{ t(`notifications.task.${alert.type}`) }} <b>{{ alert.plant }}</b> ({{ monthName(alert.month) }})
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- OVERVIEW -->
      <div v-if="activeView === 'overview'" class="view-scroll">
        <header class="page-header">
          <h2>{{ t('overview.title') }}</h2>
          <p class="subtitle">{{ t('overview.subtitle') }}</p>
        </header>

        <div class="weather-card mb-30">
          <template v-if="weather && !weatherError">
            <div class="weather-current">
              <div class="weather-city">📍 {{ weather.cityName }}</div>
              <div class="weather-main">
                <div class="weather-icon">{{ weatherEmoji(weather.current_weather.weathercode) }}</div>
                <div class="weather-temp">{{ Math.round(weather.current_weather.temperature) }}°C</div>
              </div>
              <div class="weather-desc">{{ t('overview.current_weather') }}</div>
            </div>
            <div class="weather-forecast">
              <div v-for="n in 3" :key="n" class="forecast-card">
                <span class="fc-date">{{ weekday(weather.daily.time[n]) }}</span>
                <span class="fc-icon">{{ weatherEmoji(weather.daily.weathercode[n]) }}</span>
                <span class="fc-temp">{{ Math.round(weather.daily.temperature_2m_max[n]) }}° / {{ Math.round(weather.daily.temperature_2m_min[n]) }}°</span>
              </div>
            </div>
          </template>
          <div v-else :class="['weather-placeholder', { error: weatherError }]" @click="showView('settings')">
            <span class="placeholder-icon">{{ weatherError ? '⚠️' : '🌤️' }}</span>
            <div class="placeholder-text">
              <strong>{{ weatherError ? t('overview.city_not_found') : t('overview.setup_weather') }}</strong>
              <p v-if="weatherError">{{ t('overview.check_spelling') }}</p>
            </div>
          </div>
        </div>

        <div class="stats-dashboard mt-30 block-mobile">
          <div class="stat-box full-width"><span class="stat-value">{{ totalPlants }}</span><span class="stat-label">{{ t('overview.stats.planted') }}</span></div>
          <div class="stat-box full-width"><span class="stat-value">{{ totalSeedlings }}</span><span class="stat-label">{{ t('overview.stats.seedlings') }}</span></div>
          <div class="stat-box full-width"><span class="stat-value">{{ pots.length }}</span><span class="stat-label">{{ t('overview.stats.pots') }}</span></div>
          <div class="stat-box full-width"><span class="stat-value">{{ usedBeds }} / {{ totalBeds }}</span><span class="stat-label">{{ t('overview.stats.beds') }}</span></div>
        </div>

        <h3 class="section-title mt-30">{{ t('overview.crops_title') }}</h3>
        <div class="section-block mb-30">
          <div v-if="plantedCrops.length === 0" class="empty-state"><div class="empty-state-icon">🪴</div><h3>{{ t('overview.empty_garden') }}</h3></div>
          <div class="card-grid" v-else>
            <div v-for="crop in plantedCrops" :key="crop.id" class="card">
              <div class="card-body">
                <div class="card-top align-center">
                  <div class="card-icon-small">{{ crop.icon }}</div>
                  <div class="card-title flex-grow"><h3>{{ crop.name }}</h3><span class="badge">{{ categoryLabel(crop.category) }}</span></div>
                  <div class="quantity-bubble"><span class="qty-value">{{ crop.quantity }}</span><span class="qty-label">{{ t('overview.plants') }}</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <template v-if="pots.length > 0">
          <h3 class="section-title mt-30">{{ t('overview.pots_title') }}</h3>
          <div class="section-block mb-30">
            <div class="card-grid">
              <div v-for="pot in pots" :key="'recap' + pot.id" class="card">
                <div class="card-body">
                  <div class="card-top align-center">
                    <div class="card-icon-small">{{ pot.icon }}</div>
                    <div class="card-title flex-grow"><h3>{{ pot.name }}</h3>
                      <span :class="['badge', pot.environment === 'indoor' ? 'badge-indoor' : 'badge-outdoor']" style="margin-top:5px;">{{ pot.environment === 'indoor' ? '🏠 ' + t('pots.indoor') : '☀️ ' + t('pots.outdoor') }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- HOME ASSISTANT -->
      <div v-if="activeView === 'homeassistant'" class="view-scroll">
        <header class="page-header">
          <h2>Home Assistant</h2>
          <p class="subtitle">{{ t('ha.subtitle') }}</p>
        </header>

        <h3 class="section-title">{{ t('ha.setup_title') }}</h3>
        <div class="ha-steps mb-30">
          <div class="ha-step">
            <div class="step-number">1</div>
            <div class="step-body">
              <h4>{{ t('ha.step1.title') }}</h4>
              <p v-html="t('ha.step1.hacs_html')"></p>
              <div class="copy-field"><code>{{ HA_REPOSITORY }}</code><button class="btn-icon" @click="copy(HA_REPOSITORY, 'repo')" :title="t('common.copy')">{{ recentlyCopied === 'repo' ? '✓' : '⧉' }}</button></div>
              <p v-html="t('ha.step1.manual_html')"></p>
              <p>{{ t('ha.step1.restart') }}</p>
            </div>
          </div>
          <div class="ha-step">
            <div class="step-number">2</div>
            <div class="step-body">
              <h4>{{ t('ha.step2.title') }}</h4>
              <p>{{ t('ha.step2.text') }}</p>
              <template v-if="haKey">
                <div class="new-key-box">
                  <code>{{ haKey }}</code>
                  <button class="btn-icon" @click="copy(haKey, 'hakey')" :title="t('common.copy')">{{ recentlyCopied === 'hakey' ? '✓' : '⧉' }}</button>
                </div>
                <p class="field-help">{{ t('apikeys.copy_now') }}</p>
              </template>
              <button v-else class="btn-submit" @click="createHaKey" :disabled="creatingKey">{{ t('ha.step2.create') }}</button>
              <p class="field-help mt-15" v-html="t('ha.step2.manage_html')"></p>
            </div>
          </div>
          <div class="ha-step">
            <div class="step-number">3</div>
            <div class="step-body">
              <h4>{{ t('ha.step3.title') }}</h4>
              <p v-html="t('ha.step3.text_html')"></p>
              <div class="copy-field"><code>{{ serverUrl }}</code><button class="btn-icon" @click="copy(serverUrl, 'url')" :title="t('common.copy')">{{ recentlyCopied === 'url' ? '✓' : '⧉' }}</button></div>
              <p class="field-help" v-html="t('ha.step3.url_help_html')"></p>
            </div>
          </div>
        </div>

        <h3 class="section-title">{{ t('ha.entities_title') }}</h3>
        <p class="subtitle mb-15">{{ t('ha.entities_help') }}</p>
        <div class="table-responsive mb-30">
          <table class="data-table table-ha">
            <thead><tr><th>{{ t('ha.device') }}</th><th>{{ t('ha.entities') }}</th></tr></thead>
            <tbody>
              <tr>
                <td><strong>{{ t('ha.names.garden') }}</strong></td>
                <td class="entity-list">
                  <code v-for="e in gardenEntities" :key="e">{{ e }}</code>
                </td>
              </tr>
              <tr>
                <td><strong>{{ t('ha.names.seedlings') }}</strong></td>
                <td class="entity-list">
                  <code v-for="e in seedlingEntities" :key="e">{{ e }}</code>
                </td>
              </tr>
              <tr v-for="d in haDevices" :key="d.key">
                <td>
                  <strong>{{ d.name }}</strong>
                  <div class="ha-device-meta"><span class="badge">{{ d.kind === 'bed' ? t('ha.bed') : t('ha.pot') }}</span><span v-if="d.thirsty" class="badge badge-expired">{{ t('pots.thirsty') }}</span></div>
                </td>
                <td class="entity-list">
                  <code v-for="e in d.entities" :key="e">{{ e }}</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 class="section-title">{{ t('ha.examples_title') }}</h3>
        <div v-for="ex in haExamples" :key="ex.key" class="ha-example">
          <div class="ha-example-header">
            <div><h4>{{ ex.title }}</h4><p>{{ ex.desc }}</p></div>
            <button class="btn-cancel" @click="copy(ex.yaml, ex.key)">{{ recentlyCopied === ex.key ? t('common.copied') : t('ha.copy_yaml') }}</button>
          </div>
          <pre class="code-block"><code>{{ ex.yaml }}</code></pre>
        </div>
      </div>

      <!-- SETTINGS -->
      <div v-if="activeView === 'settings'" class="view-scroll">
        <header class="page-header"><h2>{{ t('settings.title') }}</h2></header>

        <div class="settings-grid">
          <div class="settings-card card-discord" style="grid-column: 1 / -1;">
            <div class="settings-header"><div class="settings-icon">💬</div><h3>{{ t('settings.discord.title') }}</h3></div>
            <div class="settings-body">
              <div class="form-group">
                <label>{{ t('settings.discord.url') }}</label>
                <div class="input-action flex-col-mobile">
                  <input type="url" v-model="settings.webhook_url" placeholder="https://discord.com/api/webhooks/..." />
                  <button class="btn-submit full-width-mobile" @click="testWebhook" :disabled="!settings.webhook_url">{{ t('settings.discord.test') }}</button>
                </div>
              </div>
              <div class="form-group mt-15" style="max-width: 220px;">
                <label>{{ t('settings.discord.time') }}</label>
                <input type="time" v-model="settings.webhook_time" class="full-width-mobile" />
              </div>
              <div class="form-group mt-15">
                <label class="toggle-container">
                  <input type="checkbox" v-model="settings.webhook_watering_alert">
                  <span class="toggle-slider"></span>
                  <span class="toggle-label">{{ t('settings.discord.watering_alert') }} 💦</span>
                </label>
              </div>
              <div class="form-group mt-15">
                <label class="toggle-container">
                  <input type="checkbox" v-model="settings.webhook_rain_alert">
                  <span class="toggle-slider"></span>
                  <span class="toggle-label">{{ t('settings.discord.rain_alert') }} 🌧️</span>
                </label>
              </div>
            </div>
          </div>

          <div class="settings-card card-location">
            <div class="settings-header"><div class="settings-icon">🌤️</div><h3>{{ t('settings.location.title') }}</h3></div>
            <div class="settings-body">
              <div class="form-group"><label>{{ t('settings.location.city') }}</label><input type="text" v-model="settings.city" :placeholder="t('settings.location.city_placeholder')" @blur="loadWeather" @keyup.enter="loadWeather" /></div>
              <div v-if="weatherError" class="help-text">❌ {{ t('settings.location.not_found') }}</div>
            </div>
          </div>

          <div class="settings-card card-language">
            <div class="settings-header"><div class="settings-icon">🌐</div><h3>{{ t('settings.language.title') }}</h3></div>
            <div class="settings-body">
              <p class="settings-desc">{{ t('settings.language.desc') }}</p>
              <select :value="locale" @change="changeLanguage($event.target.value)">
                <option value="en">English</option>
                <option value="fr">Français</option>
              </select>
            </div>
          </div>

          <div class="settings-card card-data">
            <div class="settings-header"><div class="settings-icon">💾</div><h3>{{ t('settings.backup.title') }}</h3></div>
            <div class="settings-body">
              <p class="settings-desc">{{ t('settings.backup.desc') }}</p>
              <div style="display:flex; gap:10px;" class="flex-col-mobile">
                <button class="btn-submit full-width-mobile" style="flex:1;" @click="exportAll">📤 {{ t('settings.backup.export') }}</button>
                <button class="btn-cancel full-width-mobile" style="flex:1;" @click="$refs.backupInput.click()">📥 {{ t('settings.backup.import') }}</button>
                <input type="file" ref="backupInput" @change="onBackupFileSelected" accept=".json" style="display: none;" />
              </div>
            </div>
          </div>

          <div class="settings-card card-security">
            <div class="settings-header"><div class="settings-icon">🔒</div><h3>{{ t('settings.account.title') }}</h3></div>
            <div class="settings-body">
              <p class="settings-desc" v-html="t('settings.account.signed_in_html', { name: escapeHtml(username) })"></p>
              <p v-if="defaultCredentials" class="settings-desc warning-text" v-html="t('security.default_credentials_html')"></p>
              <p class="settings-desc" v-else v-html="t('settings.account.change_html')"></p>
              <button class="btn-cancel full-width-mobile" @click="logout">{{ t('settings.account.logout') }}</button>
            </div>
          </div>

          <div class="settings-card card-apikeys" style="grid-column: 1 / -1;">
            <div class="settings-header"><div class="settings-icon">🔑</div><h3>{{ t('apikeys.title') }}</h3></div>
            <div class="settings-body">
              <p class="settings-desc">{{ t('apikeys.desc') }}</p>
              <form class="input-action flex-col-mobile" @submit.prevent="createApiKey(newKeyName)">
                <input type="text" v-model="newKeyName" :placeholder="t('apikeys.name_placeholder')" maxlength="60" />
                <button type="submit" class="btn-submit full-width-mobile" :disabled="creatingKey">{{ t('apikeys.create') }}</button>
              </form>
              <div v-if="createdKey" class="new-key-panel">
                <strong>{{ t('apikeys.created', { name: createdKey.name }) }}</strong>
                <div class="new-key-box">
                  <code>{{ createdKey.key }}</code>
                  <button class="btn-icon" @click="copy(createdKey.key, 'newkey')" :title="t('common.copy')">{{ recentlyCopied === 'newkey' ? '✓' : '⧉' }}</button>
                </div>
                <p class="field-help">{{ t('apikeys.copy_now') }}</p>
                <button class="btn-cancel" @click="createdKey = null">{{ t('apikeys.done') }}</button>
              </div>
              <div v-if="apiKeys.length === 0" class="empty-state-small">{{ t('apikeys.empty') }}</div>
              <div v-else class="table-responsive">
                <table class="data-table">
                  <thead><tr><th>{{ t('apikeys.name') }}</th><th>{{ t('apikeys.key') }}</th><th>{{ t('apikeys.created_at') }}</th><th>{{ t('apikeys.last_used') }}</th><th></th></tr></thead>
                  <tbody>
                    <tr v-for="k in apiKeys" :key="k.id">
                      <td><strong>{{ k.name }}</strong></td>
                      <td><code>{{ k.prefix }}…</code></td>
                      <td>{{ formatDate(k.created_at) }}</td>
                      <td>{{ k.last_used_at ? formatDate(k.last_used_at) : t('apikeys.never') }}</td>
                      <td style="text-align: right;"><button class="btn-icon danger" @click="deleteApiKey(k)" :title="t('apikeys.revoke')"><Icon name="trash" :size="15" /></button></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- MODALS -->
    <div v-if="treeModal" class="modal-overlay" @click.self="treeModal = false">
      <div class="modal">
        <h3>{{ t('garden.tree_modal.title') }} 🌳</h3>
        <form @submit.prevent="addTree">
          <div class="form-group">
            <label>{{ t('garden.tree_modal.size') }}</label>
            <select v-model="newTree.size" required>
              <option v-for="s in TREE_SIZES" :key="s" :value="s">{{ t(`garden.tree_modal.sizes.${s}`) }}</option>
            </select>
          </div>
          <div class="actions block-mobile mt-30">
            <button type="button" class="btn-cancel full-width" @click="treeModal = false">{{ t('common.cancel') }}</button>
            <button type="submit" class="btn-submit full-width">{{ t('garden.place') }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="decorModal" class="modal-overlay" @click.self="decorModal = false">
      <div class="modal">
        <h3>{{ t('garden.decor_modal.title') }} ✨</h3>
        <p class="subtitle mb-15">{{ t('garden.decor_modal.desc') }}</p>
        <div class="decor-grid">
          <span v-for="emoji in DECOR_ICONS" :key="emoji" :class="['decor-option', { active: newDecor.icon === emoji }]" @click="newDecor.icon = emoji">{{ emoji }}</span>
        </div>
        <div class="actions block-mobile mt-30">
          <button type="button" class="btn-cancel full-width" @click="decorModal = false">{{ t('common.cancel') }}</button>
          <button class="btn-submit full-width" @click="addDecor" :disabled="!newDecor.icon">{{ t('garden.place') }}</button>
        </div>
      </div>
    </div>

    <div v-if="seedModal" class="modal-overlay" @click.self="seedModal = false">
      <div class="modal modal-large">
        <h3>{{ editingSeed ? t('seeds.modal.edit') : t('seeds.modal.add') }}</h3>
        <form @submit.prevent="saveSeed">
          <div class="form-row block-mobile">
            <div class="form-group icon-picker-field full-width"><label>{{ t('common.icon') }}</label><div class="icon-picker"><span v-for="ico in SEED_ICONS" :key="ico" :class="['icon-option', { 'icon-active': seedForm.icon === ico }]" @click="seedForm.icon = ico">{{ ico }}</span></div></div>
            <div class="form-group flex-grow full-width"><label>{{ t('seeds.modal.name') }} *</label><input v-model="seedForm.name" required /></div>
          </div>

          <div class="form-row block-mobile">
            <div class="form-group third full-width"><label>{{ t('seeds.modal.category') }} *</label><select v-model="seedForm.category" required><option v-for="c in CATEGORIES" :key="c" :value="c">{{ t(`category.${c}`) }}</option></select></div>
            <div class="form-group third full-width"><label>{{ t('seeds.modal.soil') }}</label><select v-model="seedForm.soil"><option value="">{{ t('seeds.modal.not_set') }}</option><option v-for="s in SOILS" :key="s" :value="s">{{ t(`soil.${s}`) }}</option></select></div>
            <div class="form-group third full-width"><label>{{ t('seeds.modal.watering') }} *</label><select v-model="seedForm.watering_interval" required><option v-for="n in WATERING_INTERVALS" :key="n" :value="n">{{ wateringLabel(n) }}</option></select></div>
          </div>

          <div class="form-row block-mobile">
            <div class="form-group flex-grow full-width" style="justify-content: center;">
              <label class="toggle-container">
                <input type="checkbox" v-model="seedForm.in_stock">
                <span class="toggle-slider"></span>
                <span class="toggle-label">{{ t('seeds.modal.in_stock') }}</span>
              </label>
              <label class="toggle-container mt-15">
                <input type="checkbox" v-model="seedForm.is_plant">
                <span class="toggle-slider"></span>
                <span class="toggle-label">{{ t('seeds.modal.is_plant') }}</span>
              </label>
            </div>
            <div class="form-group third full-width">
              <label>{{ t('seeds.modal.expiry') }}</label>
              <input type="month" v-model="seedForm.expiry" />
            </div>
          </div>

          <div class="form-row block-mobile mt-15">
            <div v-for="field in ['tray_start', 'planting_start', 'harvest_start']" :key="field" class="form-group third full-width">
              <label>{{ t(`seeds.modal.${field}`) }}</label>
              <select v-model="seedForm[field]"><option :value="null">{{ t('seeds.modal.month') }}</option><option v-for="m in 12" :key="field + m" :value="m">{{ monthName(m) }}</option></select>
            </div>
          </div>
          <div class="form-row block-mobile">
            <div v-for="field in ['tray_end', 'planting_end', 'harvest_end']" :key="field" class="form-group third full-width">
              <label>{{ t(`seeds.modal.${field}`) }}</label>
              <select v-model="seedForm[field]"><option :value="null">{{ t('seeds.modal.month') }}</option><option v-for="m in 12" :key="field + m" :value="m">{{ monthName(m) }}</option></select>
            </div>
          </div>
          <div class="actions"><button type="button" class="btn-cancel full-width" @click="seedModal = false">{{ t('common.cancel') }}</button><button type="submit" class="btn-submit full-width">{{ t('common.save') }}</button></div>
        </form>
      </div>
    </div>

    <div v-if="seedImport" class="modal-overlay" @click.self="seedImport = null">
      <div class="modal">
        <h3>{{ t('seeds.import_modal.title') }} 📥</h3>
        <p class="modal-desc" v-html="t('seeds.import_modal.desc_html', { n: seedImport.length })"></p>
        <div class="import-preview">
          <div v-for="(item, index) in seedImport.slice(0, 10)" :key="index" class="import-row">
            <span>{{ item.icon || item.icone || '🌱' }}</span>
            <strong>{{ item.name || item.nom || '?' }}</strong>
          </div>
          <div v-if="seedImport.length > 10" class="import-more">{{ t('seeds.import_modal.more', { n: seedImport.length - 10 }) }}</div>
        </div>
        <div class="actions block-mobile mt-30">
          <button type="button" class="btn-cancel full-width" @click="seedImport = null">{{ t('common.cancel') }}</button>
          <button type="button" class="btn-submit full-width" @click="confirmSeedImport">{{ t('seeds.import_modal.confirm') }}</button>
        </div>
      </div>
    </div>

    <div v-if="backupImport" class="modal-overlay" @click.self="backupImport = null">
      <div class="modal">
        <h3>{{ t('settings.restore.title') }} 📥</h3>
        <p class="modal-desc warning-text">⚠️ {{ t('settings.restore.warning') }}</p>
        <div class="import-preview">
          <ul>
            <li><strong>{{ label('settings.restore.seeds') }}</strong> {{ backupCount('seeds', 'grainotheque') }}</li>
            <li><strong>{{ label('settings.restore.plots') }}</strong> {{ backupCount('plots', 'parcelles') }}</li>
            <li><strong>{{ label('settings.restore.seedlings') }}</strong> {{ backupCount('seedlings', 'godets') }}</li>
            <li><strong>{{ label('settings.restore.pots') }}</strong> {{ backupCount('pots', 'pots') }}</li>
          </ul>
        </div>
        <div class="actions block-mobile mt-30">
          <button type="button" class="btn-cancel full-width" @click="backupImport = null">{{ t('common.cancel') }}</button>
          <button type="button" class="btn-submit btn-danger full-width" @click="confirmBackupImport">{{ t('settings.restore.confirm') }}</button>
        </div>
      </div>
    </div>

    <div v-if="seedlingModal" class="modal-overlay" @click.self="seedlingModal = false">
      <div class="modal">
        <h3>{{ seedlingForm.id ? t('seedlings.modal.edit') : t('seedlings.modal.add') }}</h3>
        <form @submit.prevent="saveSeedling">
          <div class="form-group">
            <label>{{ t('seedlings.modal.seed') }} *</label>
            <select v-model="seedlingForm.seed_id" required>
              <option disabled value="">{{ t('common.choose') }}</option>
              <option v-for="s in seeds" :key="'sl' + s.id" :value="s.id">{{ s.icon }} {{ s.name }}</option>
            </select>
          </div>
          <div class="form-group mt-15"><label>{{ t('seedlings.modal.quantity') }} *</label><input type="number" v-model.number="seedlingForm.quantity" min="1" max="500" required /></div>
          <div class="form-group mt-15"><label>{{ t('seedlings.modal.location') }}</label><input type="text" v-model="seedlingForm.location" :placeholder="t('seedlings.modal.location_placeholder')" /></div>
          <div class="actions block-mobile">
            <button type="button" class="btn-cancel full-width" @click="seedlingModal = false">{{ t('common.cancel') }}</button>
            <button type="submit" class="btn-submit full-width" :disabled="seeds.length === 0">{{ seedlingForm.id ? t('common.update') : t('seedlings.modal.sow') }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="potModal" class="modal-overlay" @click.self="potModal = false">
      <div class="modal modal-large">
        <h3>{{ editingPot ? t('pots.modal.edit') : t('pots.modal.add') }}</h3>
        <form @submit.prevent="savePot">
          <div class="form-row block-mobile">
            <div class="form-group icon-picker-field full-width">
              <label>{{ t('common.icon') }}</label>
              <div class="icon-picker">
                <span v-for="ico in POT_ICONS" :key="ico" :class="['icon-option', { 'icon-active': potForm.icon === ico }]" @click="potForm.icon = ico">{{ ico }}</span>
              </div>
            </div>
            <div class="form-group flex-grow full-width">
              <label>{{ t('pots.modal.name') }} *</label>
              <input v-model="potForm.name" required :placeholder="t('pots.modal.name_placeholder')" />
            </div>
          </div>
          <div class="form-row block-mobile">
            <div class="form-group half full-width">
              <label>{{ t('pots.modal.environment') }} *</label>
              <select v-model="potForm.environment" required>
                <option value="indoor">🏠 {{ t('pots.indoor') }}</option>
                <option value="outdoor">☀️ {{ t('pots.outdoor') }}</option>
              </select>
            </div>
            <div class="form-group half full-width">
              <label>{{ t('seeds.modal.watering') }} *</label>
              <select v-model="potForm.watering_interval" required>
                <option v-for="n in WATERING_INTERVALS" :key="n" :value="n">{{ wateringLabel(n) }}</option>
              </select>
            </div>
          </div>
          <div class="form-group mt-15">
            <label>{{ t('pots.modal.location') }}</label>
            <input type="text" v-model="potForm.location" :placeholder="t('pots.modal.location_placeholder')" />
          </div>
          <div class="actions block-mobile mt-30">
            <button type="button" class="btn-cancel full-width" @click="potModal = false">{{ t('common.cancel') }}</button>
            <button type="submit" class="btn-submit full-width">{{ editingPot ? t('common.update') : t('pots.modal.add_button') }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="plantingBed" class="modal-overlay" @click.self="plantingBed = null">
      <div class="modal">
        <h3>{{ t('garden.planting.title') }}</h3>
        <form @submit.prevent="savePlanting">
          <div class="form-group">
            <label>{{ t('garden.planting.variety') }}</label>
            <select v-model="plantingForm.seed" required>
              <option disabled :value="null">{{ t('common.choose') }}</option>
              <option v-for="s in seeds" :key="'p' + s.id" :value="s">{{ s.icon }} {{ s.name }}</option>
            </select>
          </div>
          <template v-if="plantingForm.seed">
            <div v-if="companionCheck.good.length > 0" class="companion-alert box-good">
              <span class="companion-icon">✨</span> <div><strong>{{ t('garden.planting.good_title') }}</strong><br>{{ t('garden.planting.good_text', { names: companionCheck.good.join(', ') }) }}</div>
            </div>
            <div v-if="companionCheck.bad.length > 0" class="companion-alert box-bad">
              <span class="companion-icon">⚠️</span> <div><strong>{{ t('garden.planting.bad_title') }}</strong><br>{{ t('garden.planting.bad_text', { names: companionCheck.bad.join(', ') }) }}</div>
            </div>
          </template>
          <div class="form-group mt-15"><label>{{ t('garden.planting.quantity') }}</label><input type="number" v-model.number="plantingForm.quantity" min="1" max="1000" required /></div>
          <div class="actions block-mobile"><button type="button" class="btn-cancel full-width" @click="plantingBed = null">{{ t('common.cancel') }}</button><button type="submit" class="btn-submit full-width">{{ t('garden.planting.submit') }}</button></div>
        </form>
      </div>
    </div>

    <div v-if="managedBed" class="modal-overlay" @click.self="managedBed = null">
      <div class="modal modal-large">
        <h3>{{ t('garden.manage.title') }}</h3>
        <div class="form-group mb-15"><label>{{ t('garden.manage.name') }}</label><input type="text" v-model="managedBed.name" :placeholder="t('garden.manage.name_placeholder')" /></div>
        <p class="modal-desc">{{ t('garden.manage.desc') }}</p>
        <div v-if="managedBed.plantings.length === 0" class="empty-state-small">{{ t('garden.manage.empty') }}</div>
        <div class="manage-list" v-else>
          <div v-for="(plant, i) in managedBed.plantings" :key="i" class="manage-item block-mobile">
            <div class="item-info">
              <span class="item-icon">{{ plant.icon }}</span>
              <div class="item-details-flex">
                <span>{{ plant.name }}</span>
                <input type="month" v-model="plant.planted_on" class="input-date-small" :title="t('garden.manage.planted_on')" />
              </div>
            </div>
            <div class="item-actions mt-mobile">
              <input type="number" v-model.number="plant.quantity" min="1" class="input-qty-small" />
              <button class="btn-icon danger" @click="removePlanting(i)">×</button>
            </div>
          </div>
        </div>
        <div class="actions mt-30 block-mobile"><button type="button" class="btn-submit full-width" @click="managedBed = null">{{ t('common.done') }}</button></div>
      </div>
    </div>

    <div v-if="confirmDialog" class="modal-overlay" style="z-index: 9999;" @click.self="confirmDialog = null">
      <div class="modal modal-confirm">
        <div class="confirm-icon">{{ confirmDialog.action ? '⚠️' : 'ℹ️' }}</div>
        <h3>{{ confirmDialog.action ? t('common.confirm_title') : t('common.info_title') }}</h3>
        <p class="modal-desc" style="text-align: center;">{{ confirmDialog.message }}</p>
        <div class="actions">
          <template v-if="confirmDialog.action">
            <button type="button" class="btn-cancel" @click="confirmDialog = null">{{ t('common.cancel') }}</button>
            <button type="button" class="btn-submit btn-danger" @click="runConfirm">{{ t('common.yes') }}</button>
          </template>
          <button v-else type="button" class="btn-submit" @click="confirmDialog = null">{{ t('common.ok') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import logoImg from './assets/logo.png';
import { Icon } from './icons.js';
import { t, locale, setLocale, LOCALES } from './i18n.js';
import {
  CATEGORIES, SOILS, WATERING_INTERVALS, TREE_SIZES, SEED_ICONS, DECOR_ICONS, POT_ICONS,
  COMPANIONS, ROTATION, FAMILY_NEEDS, SOIL_TIPS, plantName, findPlant, companionship,
} from './reference.js';

const NAV = [
  { view: 'garden', icon: 'map' },
  { view: 'seeds', icon: 'book' },
  { view: 'seedlings', icon: 'sprout' },
  { view: 'pots', icon: 'pot' },
  { view: 'companions', icon: 'heart' },
  { view: 'rotation', icon: 'rotate' },
  { view: 'notifications', icon: 'bell' },
  { view: 'overview', icon: 'dashboard' },
  { view: 'homeassistant', icon: 'home' },
  { view: 'settings', icon: 'settings' },
];
const DAY_MS = 1000 * 3600 * 24;
const DEFAULT_WATERING_INTERVAL = 7;

// --- Layout ---
const activeView = ref('garden');
const menuCollapsed = ref(false);
const mobileMenuOpen = ref(false);
function showView(view) { activeView.value = view; mobileMenuOpen.value = false; }

// --- Garden data ---
const seeds = ref([]);
const plots = ref([]);
const seedlings = ref([]);
const pots = ref([]);
const settings = ref({ webhook_url: '', webhook_watering_alert: true, webhook_rain_alert: true, webhook_time: '10:00', city: '', language: locale.value });

// --- Confirmation / information dialog ---
const confirmDialog = ref(null);
function askConfirmation(message, action) { confirmDialog.value = { message, action }; }
function showInfo(message) { confirmDialog.value = { message, action: null }; }
function runConfirm() { const action = confirmDialog.value?.action; confirmDialog.value = null; if (action) action(); }

// --- Formatting helpers ---
const capitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);
const monthName = (m) => capitalize(new Date(2000, m - 1, 1).toLocaleDateString(locale.value, { month: 'long' }));
const shortMonth = (m) => capitalize(new Date(2000, m - 1, 1).toLocaleDateString(locale.value, { month: 'short' }));
const weekday = (dateStr) => new Date(dateStr).toLocaleDateString(locale.value, { weekday: 'short' });
const formatDate = (ms) => new Date(ms).toLocaleDateString(locale.value, { day: 'numeric', month: 'short', year: 'numeric' });
const currentYearMonth = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`; };
const escapeHtml = (text) => String(text ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function formatMonthYear(yyyymm) {
  const [year, month] = (yyyymm || '').split('-').map(Number);
  if (!year || !month) return t('common.unknown_date');
  return `${monthName(month)} ${year}`;
}
function wateringLabel(days) { return WATERING_INTERVALS.includes(days) ? t(`watering.${days}`) : t('watering.custom', { n: days }); }
function categoryLabel(category) { return category ? t(`category.${category}`, {}, category) : t('common.unknown'); }
// French typography puts a space before the colon
function label(key) { return t('common.label', { text: t(key) }); }
function isExpired(expiry) { return Boolean(expiry) && expiry < currentYearMonth(); }

// --- Authentication ---
const SESSION_KEY = 'msg_session';
function readSession() { try { return localStorage.getItem(SESSION_KEY) || ''; } catch (e) { return ''; } }
const sessionToken = ref(readSession());
const needsLogin = ref(false);
const loginForm = ref({ username: '', password: '' });
const loginError = ref('');
const loggingIn = ref(false);
const username = ref('');
const defaultCredentials = ref(false);

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}), Authorization: `Bearer ${sessionToken.value}` };
  if (options.json !== undefined) {
    headers['Content-Type'] = 'application/json';
    options = { ...options, body: options.json };
  }
  const res = await fetch(path, { ...options, headers });
  if (res.status === 401) requireLogin();
  return res;
}

function requireLogin() {
  sessionToken.value = '';
  try { localStorage.removeItem(SESSION_KEY); } catch (e) {}
  needsLogin.value = true;
}

async function login() {
  loginError.value = '';
  loggingIn.value = true;
  try {
    const res = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(loginForm.value) });
    if (!res.ok) { loginError.value = t('login.invalid'); return; }
    const { token } = await res.json();
    sessionToken.value = token;
    try { localStorage.setItem(SESSION_KEY, token); } catch (e) {}
    needsLogin.value = false;
    loginForm.value = { username: '', password: '' };
    await loadAll();
  } catch (e) {
    loginError.value = t('login.unreachable');
  } finally {
    loggingIn.value = false;
  }
}

async function logout() {
  try { await api('/api/auth/logout', { method: 'POST' }); } catch (e) {}
  requireLogin();
  window.location.reload();
}

// --- Synchronisation with the server ---
// Keys starting with "_" are UI-only state (e.g. the watering animation) and are never saved
const serialize = (data) => JSON.stringify(data, (key, value) => (key.startsWith('_') ? undefined : value));
function debounce(fn, delay) { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); }; }

function createSync(path, cacheKey) {
  let lastSaved = null;
  const save = debounce(async (data) => {
    const body = serialize(data);
    if (body === lastSaved) return;
    try { if (cacheKey) localStorage.setItem(cacheKey, body); } catch (e) {}
    try {
      const res = await api(path, { method: 'PUT', json: body });
      if (res.ok) lastSaved = body;
    } catch (e) {}
  }, 800);
  return { save, markSaved: (data) => { lastSaved = serialize(data); } };
}

const syncs = {
  seeds: createSync('/api/seeds', 'msg_cache_seeds'),
  plots: createSync('/api/plots', 'msg_cache_plots'),
  seedlings: createSync('/api/seedlings', 'msg_cache_seedlings'),
  pots: createSync('/api/pots', 'msg_cache_pots'),
  settings: createSync('/api/settings', null),
};
const collections = { seeds, plots, seedlings, pots, settings };
for (const [name, store] of Object.entries(collections)) {
  watch(store, (value) => syncs[name].save(value), { deep: true });
}

async function loadCollection(name) {
  const store = collections[name];
  try {
    const res = await api(`/api/${name}`);
    if (!res.ok) return;
    const data = await res.json();
    store.value = name === 'settings' ? { ...store.value, ...data } : data;
  } catch (e) {
    // Server unreachable: fall back to the copy cached in this browser
    try { const cached = localStorage.getItem(`msg_cache_${name}`); if (cached) store.value = JSON.parse(cached); } catch (_) {}
  }
  syncs[name].markSaved(store.value);
}

async function loadAll() {
  await Promise.all(Object.keys(collections).map(loadCollection));
  if (settings.value.language && settings.value.language !== locale.value) setLocale(settings.value.language);
  if (settings.value.city) loadWeather();
  loadAccount();
  loadApiKeys();
}

async function loadAccount() {
  try {
    const res = await api('/api/auth/me');
    if (res.ok) { const me = await res.json(); username.value = me.username; defaultCredentials.value = me.default_credentials; }
  } catch (e) {}
}

onMounted(() => {
  if (sessionToken.value) loadAll();
  else needsLogin.value = true;
});

function changeLanguage(value) {
  setLocale(value);
  settings.value.language = value;
}

// --- Watering ---
function daysSince(ms) { return (Date.now() - (ms || 0)) / DAY_MS; }

function bedNeedsWater(bed) {
  if (!bed || bed.type !== 'bed' || !bed.plantings?.length) return false;
  const intervals = bed.plantings
    .map(p => seeds.value.find(s => s.id === p.seed_id)?.watering_interval)
    .filter(n => n > 0);
  const interval = intervals.length ? Math.min(...intervals) : DEFAULT_WATERING_INTERVAL;
  return daysSince(bed.last_watered) >= interval;
}
function potNeedsWater(pot) { return pot.watering_interval > 0 && daysSince(pot.last_watered) >= pot.watering_interval; }

function animateWatering(item) {
  item._watering = true;
  item.last_watered = Date.now();
  setTimeout(() => { item._watering = false; }, 2000);
}
function waterBed(bed) { animateWatering(bed); }
function waterPot(pot) { animateWatering(pot); }

const globalRain = ref(false);
function waterEverything() {
  globalRain.value = true;
  plots.value.filter(bedNeedsWater).forEach(animateWatering);
  pots.value.filter(potNeedsWater).forEach(animateWatering);
  setTimeout(() => { globalRain.value = false; }, 2500);
}

const bedAlerts = computed(() => plots.value.filter(bedNeedsWater).map(bed => ({ bed, days: Math.floor(daysSince(bed.last_watered)) })));
const potAlerts = computed(() => pots.value.filter(potNeedsWater).map(pot => ({
  pot,
  days: Math.floor(daysSince(pot.last_watered)),
  place: t(`pots.${pot.environment}`) + (pot.location ? ` - ${pot.location}` : ''),
})));
const thirstyCount = computed(() => bedAlerts.value.length + potAlerts.value.length);

const calendarAlerts = computed(() => {
  const current = new Date().getMonth() + 1;
  const alerts = [];
  for (const seed of seeds.value) {
    for (const [type, month] of [['tray', seed.tray_start], ['planting', seed.planting_start]]) {
      if (!month) continue;
      const distance = (month - current + 12) % 12;
      if (distance <= 1) alerts.push({ type, plant: seed.name, icon: seed.icon, distance, month });
    }
  }
  return alerts.sort((a, b) => a.distance - b.distance);
});
const alertCount = computed(() => thirstyCount.value + calendarAlerts.value.length);

// --- Seed library ---
const seedSearch = ref('');
const seedCategoryFilter = ref('');
const seedStockFilter = ref('all');
const filteredSeeds = computed(() => seeds.value.filter(s => {
  const matchesName = (s.name || '').toLowerCase().includes(seedSearch.value.toLowerCase());
  const matchesCategory = !seedCategoryFilter.value || s.category === seedCategoryFilter.value;
  const matchesStock = seedStockFilter.value === 'all' || (seedStockFilter.value === 'in_stock' ? s.in_stock : !s.in_stock);
  return matchesName && matchesCategory && matchesStock;
}));

const EMPTY_SEED = {
  id: null, name: '', category: 'fruit_vegetable', icon: '🌱', soil: '', watering_interval: DEFAULT_WATERING_INTERVAL,
  tray_start: null, tray_end: null, planting_start: null, planting_end: null, harvest_start: null, harvest_end: null,
  in_stock: true, expiry: '', is_plant: false,
};
const seedModal = ref(false);
const editingSeed = ref(false);
const seedForm = ref({ ...EMPTY_SEED });
function openSeedModal(seed = null) {
  editingSeed.value = Boolean(seed);
  seedForm.value = seed ? { ...seed } : { ...EMPTY_SEED };
  seedModal.value = true;
}
function saveSeed() {
  if (editingSeed.value) {
    const index = seeds.value.findIndex(s => s.id === seedForm.value.id);
    if (index !== -1) seeds.value[index] = { ...seedForm.value };
  } else {
    seeds.value.push({ ...seedForm.value, id: Date.now() });
  }
  seedModal.value = false;
}
function deleteSeed(id) {
  askConfirmation(t('seeds.confirm_delete'), () => { seeds.value = seeds.value.filter(s => s.id !== id); });
}
function isInTray(seedId) { return seedlings.value.some(s => s.seed_id === seedId); }

// --- Import / export ---
function downloadJson(data, filename) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
const today = () => new Date().toISOString().split('T')[0];

function readJsonFile(event, onLoaded) {
  const input = event.target;
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    try { onLoaded(JSON.parse(e.target.result)); } catch (err) { showInfo(t('common.unreadable_file')); }
    input.value = '';
  };
  reader.readAsText(file);
}

function exportSeeds() { downloadJson(JSON.parse(serialize(seeds.value)), `seeds_${today()}.json`); }

const seedImport = ref(null);
function onSeedFileSelected(event) {
  readJsonFile(event, (parsed) => {
    if (Array.isArray(parsed)) seedImport.value = parsed;
    else showInfo(t('seeds.import_modal.invalid'));
  });
}
async function confirmSeedImport() {
  const items = seedImport.value;
  seedImport.value = null;
  const res = await api('/api/import/seeds', { method: 'POST', json: JSON.stringify(items) });
  if (res.ok) await loadCollection('seeds');
  else showInfo(t('common.import_failed'));
}

function exportAll() {
  const backup = { version: 2, exported_at: new Date().toISOString(), seeds: seeds.value, plots: plots.value, seedlings: seedlings.value, pots: pots.value };
  downloadJson(JSON.parse(serialize(backup)), `mysecretgarden_backup_${today()}.json`);
}

const backupImport = ref(null);
function onBackupFileSelected(event) {
  readJsonFile(event, (parsed) => {
    const isBackup = parsed && typeof parsed === 'object' && ['seeds', 'plots', 'grainotheque', 'parcelles'].some(k => k in parsed);
    if (isBackup) backupImport.value = parsed;
    else showInfo(t('settings.restore.invalid'));
  });
}
function backupCount(key, legacyKey) { return (backupImport.value?.[key] ?? backupImport.value?.[legacyKey] ?? []).length; }
async function confirmBackupImport() {
  const payload = backupImport.value;
  backupImport.value = null;
  const res = await api('/api/import', { method: 'POST', json: JSON.stringify(payload) });
  if (!res.ok) { showInfo(t('common.import_failed')); return; }
  await Promise.all(['seeds', 'plots', 'seedlings', 'pots'].map(loadCollection));
  recenter();
}

// --- Seedlings ---
const seedlingCards = computed(() => seedlings.value.map(s => {
  const seed = seeds.value.find(x => x.id === s.seed_id);
  return { ...s, name: seed?.name ?? t('seedlings.deleted_seed'), icon: seed?.icon ?? '❓', category: seed?.category };
}).reverse());
const totalSeedlings = computed(() => seedlings.value.reduce((sum, s) => sum + (Number(s.quantity) || 0), 0));

const seedlingModal = ref(false);
const seedlingForm = ref({});
function openSeedlingModal(seedling = null) {
  seedlingForm.value = seedling
    ? { id: seedling.id, seed_id: seedling.seed_id, quantity: seedling.quantity, location: seedling.location }
    : { id: null, seed_id: '', quantity: 1, location: '' };
  seedlingModal.value = true;
}
function saveSeedling() {
  if (seedlingForm.value.id) {
    const index = seedlings.value.findIndex(s => s.id === seedlingForm.value.id);
    if (index !== -1) seedlings.value[index] = { ...seedlingForm.value };
  } else {
    seedlings.value.push({ ...seedlingForm.value, id: Date.now() });
  }
  seedlingModal.value = false;
}
function deleteSeedling(id) {
  askConfirmation(t('seedlings.confirm_delete'), () => { seedlings.value = seedlings.value.filter(s => s.id !== id); });
}

// --- Pots ---
const potSearch = ref('');
const potGroups = computed(() => ['indoor', 'outdoor'].map(environment => ({
  environment,
  pots: pots.value.filter(p => p.environment === environment && (p.name || '').toLowerCase().includes(potSearch.value.toLowerCase())),
})));

const EMPTY_POT = { id: null, name: '', icon: '🪴', environment: 'indoor', location: '', watering_interval: DEFAULT_WATERING_INTERVAL, last_watered: 0 };
const potModal = ref(false);
const editingPot = ref(false);
const potForm = ref({ ...EMPTY_POT });
function openPotModal(pot = null) {
  editingPot.value = Boolean(pot);
  potForm.value = pot ? { ...pot } : { ...EMPTY_POT, id: Date.now(), last_watered: Date.now() };
  potModal.value = true;
}
function savePot() {
  if (editingPot.value) {
    const index = pots.value.findIndex(p => p.id === potForm.value.id);
    if (index !== -1) pots.value[index] = { ...potForm.value };
  } else {
    pots.value.push({ ...potForm.value });
  }
  potModal.value = false;
}
function deletePot(id) {
  askConfirmation(t('pots.confirm_delete'), () => { pots.value = pots.value.filter(p => p.id !== id); });
}

// --- Companion planting ---
const companionSearch = ref('');
const filteredCompanions = computed(() => {
  const query = companionSearch.value.trim().toLowerCase();
  const sorted = [...COMPANIONS].sort((a, b) => plantName(a.plant, locale.value).localeCompare(plantName(b.plant, locale.value), locale.value));
  if (!query) return sorted;
  return sorted.filter(c => plantName(c.plant, locale.value).toLowerCase().includes(query) || findPlant(query) === c.plant);
});

function plantNamesIn(bed) { return [...new Set((bed?.plantings || []).map(p => p.name))]; }

function hasConflict(bed) {
  if (!bed || bed.type !== 'bed') return false;
  const names = plantNamesIn(bed);
  return names.some((a, i) => names.slice(i + 1).some(b => companionship(a, b).bad));
}

// --- Garden plan: canvas ---
const zoom = ref(1);
function zoomBy(delta) { zoom.value = Math.min(Math.max(0.2, zoom.value + delta), 3); }
function onWheel(e) { zoomBy(e.deltaY < 0 ? 0.05 : -0.05); }

const activeTool = ref('hand');
const canvasRef = ref(null);
const pan = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const lastPointer = ref({ x: 0, y: 0 });
const isDrawing = ref(false);
const startPoint = ref({ x: 0, y: 0 });
const drawingPlot = ref(null);
const draggedPlot = ref(null);
const resizedPlot = ref(null);
const resizedBorder = ref(null);
const dragOffset = ref({ x: 0, y: 0 });
const pinchStart = ref(null);
const PIXELS_PER_METER = 40;
const SNAP = 4; // 10 cm

const snap = (value) => Math.round(value / SNAP) * SNAP;
const toCm = (pixels) => Math.round((pixels / PIXELS_PER_METER) * 100);

function plotStyle(p) {
  if (p.type === 'border') {
    const length = Math.hypot(p.x2 - p.x1, p.y2 - p.y1);
    const angle = Math.atan2(p.y2 - p.y1, p.x2 - p.x1) * (180 / Math.PI);
    return { left: p.x1 + 'px', top: p.y1 + 'px', width: length + 'px', transform: `rotate(${angle}deg)` };
  }
  if (p.type === 'tree' || p.type === 'decor') return { left: p.x + 'px', top: p.y + 'px' };
  return { left: p.x + 'px', top: p.y + 'px', width: p.width + 'px', height: p.height + 'px' };
}
function actionsStyle(p) {
  if (p.type !== 'border') return {};
  const angle = Math.atan2(p.y2 - p.y1, p.x2 - p.x1) * (180 / Math.PI);
  return { transform: `translateX(-50%) rotate(${-angle}deg)` };
}

function recenter() { pan.value = { x: 0, y: 0 }; zoom.value = 1; }
function goToBed(bed) {
  pan.value = { x: -bed.x + window.innerWidth / 2 - 140, y: -bed.y + window.innerHeight / 2 };
  zoom.value = 1.2;
  showView('garden');
}

function deletePlot(id) {
  askConfirmation(t('garden.confirm_delete'), () => {
    plots.value = plots.value.filter(p => p.id !== id);
    if (historyPlot.value?.id === id) closeHistory();
  });
}

function pointerPosition(e) {
  const point = e.touches?.length ? e.touches[0] : e;
  return { x: point.clientX, y: point.clientY };
}
function canvasPosition(e) {
  const pointer = pointerPosition(e);
  const rect = canvasRef.value.getBoundingClientRect();
  return { x: (pointer.x - rect.left) / zoom.value, y: (pointer.y - rect.top) / zoom.value };
}

const treeModal = ref(false);
const decorModal = ref(false);
const newPlotPosition = ref({ x: 0, y: 0 });
const newTree = ref({ size: 'medium' });
const newDecor = ref({ icon: '' });

function startAction(e) {
  if (e.touches?.length === 2) {
    const [a, b] = e.touches;
    pinchStart.value = { distance: Math.hypot(b.clientX - a.clientX, b.clientY - a.clientY), zoom: zoom.value };
    isPanning.value = false; isDrawing.value = false; drawingPlot.value = null; draggedPlot.value = null; resizedPlot.value = null;
    return;
  }
  const pos = canvasPosition(e);
  if (activeTool.value === 'hand') {
    isPanning.value = true;
    lastPointer.value = pointerPosition(e);
  } else if (activeTool.value === 'tree' || activeTool.value === 'decor') {
    newPlotPosition.value = { x: snap(pos.x), y: snap(pos.y) };
    if (activeTool.value === 'tree') { newTree.value = { size: 'medium' }; treeModal.value = true; }
    else { newDecor.value = { icon: '' }; decorModal.value = true; }
    activeTool.value = 'hand';
  } else if (activeTool.value === 'border') {
    isDrawing.value = true;
    drawingPlot.value = { type: 'border', x1: pos.x, y1: pos.y, x2: pos.x, y2: pos.y };
  } else if (activeTool.value === 'bed') {
    isDrawing.value = true;
    startPoint.value = pos;
    drawingPlot.value = { type: 'bed', name: '', x: pos.x, y: pos.y, width: 0, height: 0, size_x_cm: 0, size_y_cm: 0, plantings: [], archive: [], last_watered: Date.now() };
  }
}

function addTree() {
  plots.value.push({ id: Date.now(), type: 'tree', name: '', size: newTree.value.size, ...newPlotPosition.value });
  treeModal.value = false;
}
function addDecor() {
  plots.value.push({ id: Date.now(), type: 'decor', name: '', icon: newDecor.value.icon, ...newPlotPosition.value });
  decorModal.value = false;
}

function startDrag(e, p) {
  if (activeTool.value !== 'hand') return;
  draggedPlot.value = p;
  const pos = canvasPosition(e);
  dragOffset.value = p.type === 'border' ? { x: pos.x - p.x1, y: pos.y - p.y1 } : { x: pos.x - p.x, y: pos.y - p.y };
}

function startResize(e, p) {
  if (p.type === 'border') { resizedBorder.value = p; return; }
  resizedPlot.value = p;
  const pos = canvasPosition(e);
  startPoint.value = { ...pos, width: p.width, height: p.height };
}

function setBedSize(bed, width, height) {
  bed.width = Math.max(40, snap(width));
  bed.height = Math.max(40, snap(height));
  bed.size_x_cm = toCm(bed.width);
  bed.size_y_cm = toCm(bed.height);
}

function moveAction(e) {
  if (e.touches?.length === 2) {
    if (pinchStart.value) {
      const [a, b] = e.touches;
      const ratio = Math.hypot(b.clientX - a.clientX, b.clientY - a.clientY) / pinchStart.value.distance;
      zoom.value = Math.min(Math.max(0.2, pinchStart.value.zoom * ratio), 3);
    }
    return;
  }
  if (pinchStart.value && e.touches?.length === 1) {
    lastPointer.value = pointerPosition(e);
    pinchStart.value = null;
    if (activeTool.value === 'hand') isPanning.value = true;
    return;
  }

  const pos = canvasPosition(e);
  if (isPanning.value) {
    const pointer = pointerPosition(e);
    pan.value.x += pointer.x - lastPointer.value.x;
    pan.value.y += pointer.y - lastPointer.value.y;
    lastPointer.value = pointer;
  } else if (resizedPlot.value) {
    setBedSize(resizedPlot.value, startPoint.value.width + pos.x - startPoint.value.x, startPoint.value.height + pos.y - startPoint.value.y);
  } else if (resizedBorder.value) {
    resizedBorder.value.x2 = snap(pos.x);
    resizedBorder.value.y2 = snap(pos.y);
  } else if (draggedPlot.value) {
    const x = snap(pos.x - dragOffset.value.x);
    const y = snap(pos.y - dragOffset.value.y);
    const p = draggedPlot.value;
    if (p.type === 'border') {
      const dx = x - p.x1;
      const dy = y - p.y1;
      p.x1 += dx; p.y1 += dy; p.x2 += dx; p.y2 += dy;
    } else {
      p.x = x;
      p.y = y;
    }
  } else if (isDrawing.value) {
    const p = drawingPlot.value;
    if (p.type === 'border') {
      p.x2 = pos.x;
      p.y2 = pos.y;
    } else {
      p.x = Math.min(pos.x, startPoint.value.x);
      p.y = Math.min(pos.y, startPoint.value.y);
      setBedSize(p, Math.abs(pos.x - startPoint.value.x), Math.abs(pos.y - startPoint.value.y));
    }
  }
}

function endAction() {
  isPanning.value = false; draggedPlot.value = null; resizedPlot.value = null; resizedBorder.value = null; pinchStart.value = null;
  if (!isDrawing.value) return;
  isDrawing.value = false;
  const p = drawingPlot.value;
  const longEnough = p.type === 'border' ? Math.hypot(p.x2 - p.x1, p.y2 - p.y1) > 10 : p.size_x_cm >= 20 && p.size_y_cm >= 20;
  if (longEnough) plots.value.push({ ...p, id: Date.now() });
  drawingPlot.value = null;
  activeTool.value = 'hand';
}

function plantDots(bed) {
  return (bed.plantings || []).flatMap(p => Array.from({ length: Number(p.quantity) || 0 }, () => ({ name: p.name, icon: p.icon || '🌱' })));
}
function plantGridStyle(bed) {
  const count = plantDots(bed).length;
  if (count === 0) return { display: 'none' };
  const columns = Math.ceil(Math.sqrt(count));
  const rows = Math.ceil(count / columns);
  return { display: 'grid', gridTemplateColumns: `repeat(${columns}, 1fr)`, gridTemplateRows: `repeat(${rows}, 1fr)`, width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, padding: '8px', alignItems: 'center', justifyItems: 'center', pointerEvents: 'none' };
}

// --- Planting, bed management, history ---
const plantingBed = ref(null);
const plantingForm = ref({ seed: null, quantity: 1 });
function openPlantingModal(bed) {
  if (seeds.value.length === 0) { showInfo(t('garden.planting.no_seeds')); return; }
  plantingBed.value = bed;
  plantingForm.value = { seed: null, quantity: 1 };
}
const companionCheck = computed(() => {
  const seed = plantingForm.value.seed;
  if (!plantingBed.value || !seed) return { good: [], bad: [] };
  const others = plantNamesIn(plantingBed.value);
  return {
    good: others.filter(name => companionship(seed.name, name).good),
    bad: others.filter(name => companionship(seed.name, name).bad),
  };
});
function savePlanting() {
  const { seed, quantity } = plantingForm.value;
  const bed = plantingBed.value;
  bed.plantings.push({ seed_id: seed.id, name: seed.name, icon: seed.icon, quantity, planted_on: currentYearMonth() });
  bed.last_watered = Date.now();
  plantingBed.value = null;
}

const managedBed = ref(null);
function openManageBed(bed) {
  bed.plantings.forEach(p => { if (!p.planted_on) p.planted_on = currentYearMonth(); });
  managedBed.value = bed;
}
function removePlanting(index) {
  askConfirmation(t('garden.manage.confirm_remove'), () => {
    const bed = managedBed.value;
    const [removed] = bed.plantings.splice(index, 1);
    bed.archive = [...(bed.archive || []), { ...removed, removed_on: currentYearMonth() }];
  });
}

const historyPlot = ref(null);
function openHistory(bed) { historyPlot.value = bed; }
function closeHistory() { historyPlot.value = null; }
const historyGroups = computed(() => {
  const bed = historyPlot.value;
  if (!bed) return [];
  const entries = [
    ...(bed.plantings || []).map(p => ({ ...p, active: true })),
    ...(bed.archive || []).map(p => ({ ...p, active: false })),
  ].sort((a, b) => (b.planted_on || '').localeCompare(a.planted_on || ''));
  const groups = [];
  for (const entry of entries) {
    const date = entry.planted_on || '';
    if (groups.at(-1)?.date !== date) groups.push({ date, label: formatMonthYear(date), plants: [] });
    groups.at(-1).plants.push(entry);
  }
  return groups;
});

// --- Overview ---
const plantedCrops = computed(() => {
  const crops = {};
  for (const bed of plots.value.filter(p => p.type === 'bed')) {
    for (const p of bed.plantings || []) {
      const seed = seeds.value.find(s => s.id === p.seed_id);
      crops[p.seed_id] ??= { id: p.seed_id, name: p.name, icon: p.icon, category: seed?.category, quantity: 0 };
      crops[p.seed_id].quantity += Number(p.quantity) || 0;
    }
  }
  return Object.values(crops).sort((a, b) => b.quantity - a.quantity);
});
const totalPlants = computed(() => plantedCrops.value.reduce((sum, c) => sum + c.quantity, 0));
const totalBeds = computed(() => plots.value.filter(p => p.type === 'bed').length);
const usedBeds = computed(() => plots.value.filter(p => p.type === 'bed' && p.plantings?.length).length);

// --- Weather ---
const weather = ref(null);
const weatherError = ref(false);
const frostDate = computed(() => {
  const daily = weather.value?.daily;
  if (!daily?.temperature_2m_min) return null;
  const index = daily.temperature_2m_min.findIndex(min => min <= 0);
  return index === -1 ? null : new Date(daily.time[index]).toLocaleDateString(locale.value, { day: '2-digit', month: '2-digit' });
});
async function loadWeather() {
  if (!settings.value.city) { weatherError.value = false; weather.value = null; return; }
  try {
    const query = encodeURIComponent(settings.value.city.trim());
    const geo = await (await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${query}&count=1&language=${locale.value}`)).json();
    if (!geo.results?.length) { weatherError.value = true; weather.value = null; return; }
    const { latitude, longitude, name } = geo.results[0];
    const forecast = await (await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&current_weather=true&timezone=auto&forecast_days=10`)).json();
    weather.value = { ...forecast, cityName: name };
    weatherError.value = false;
  } catch (e) { weatherError.value = true; weather.value = null; }
}
function weatherEmoji(code) {
  if (code === 0) return '☀️';
  if (code > 0 && code < 4) return '⛅';
  if (code > 44 && code < 49) return '🌫️';
  if (code > 50 && code < 68) return '🌧️';
  if (code > 70 && code < 80) return '❄️';
  if (code > 94) return '⛈️';
  return '🌤️';
}

// --- Discord ---
async function testWebhook() {
  try {
    // Save first: the server sends the test to the stored URL
    await api('/api/settings', { method: 'PUT', json: serialize(settings.value) });
    const res = await api('/api/settings/test-webhook', { method: 'POST' });
    showInfo(res.ok ? t('settings.discord.test_ok') : t('settings.discord.test_failed'));
  } catch (e) {
    showInfo(t('settings.discord.test_failed'));
  }
}

// --- API keys ---
const apiKeys = ref([]);
const newKeyName = ref('');
const createdKey = ref(null);
const creatingKey = ref(false);
const haKey = ref('');

async function loadApiKeys() {
  try { const res = await api('/api/api-keys'); if (res.ok) apiKeys.value = await res.json(); } catch (e) {}
}
async function createApiKey(name) {
  creatingKey.value = true;
  try {
    const res = await api('/api/api-keys', { method: 'POST', json: JSON.stringify({ name }) });
    if (!res.ok) { showInfo(t('apikeys.create_failed')); return null; }
    const key = await res.json();
    await loadApiKeys();
    newKeyName.value = '';
    createdKey.value = key;
    return key;
  } finally {
    creatingKey.value = false;
  }
}
async function createHaKey() {
  const key = await createApiKey('Home Assistant');
  if (key) { haKey.value = key.key; createdKey.value = null; }
}
function deleteApiKey(key) {
  askConfirmation(t('apikeys.confirm_revoke', { name: key.name }), async () => {
    await api(`/api/api-keys/${key.id}`, { method: 'DELETE' });
    if (createdKey.value?.id === key.id) createdKey.value = null;
    await loadApiKeys();
  });
}

// --- Home Assistant tab ---
const HA_REPOSITORY = 'https://github.com/emeryn/ha-mysecretgarden';
const serverUrl = window.location.origin;
const recentlyCopied = ref('');

async function copy(text, key) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (e) {
    // navigator.clipboard does not exist over plain HTTP (local IP access): fall back to execCommand
    const area = document.createElement('textarea');
    area.value = text; area.style.position = 'fixed'; area.style.opacity = '0';
    document.body.appendChild(area); area.select();
    try { document.execCommand('copy'); } catch (_) {}
    document.body.removeChild(area);
  }
  recentlyCopied.value = key;
  setTimeout(() => { if (recentlyCopied.value === key) recentlyCopied.value = ''; }, 1800);
}

// Same transformation Home Assistant uses to build entity ids (no accents, lowercase, "_")
function slug(text) {
  return String(text || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
}
// Home Assistant names entities in its own language: ids are shown for the current app language
const entityId = (domain, device, entity) => `${domain}.${slug(device)}_${slug(t(`ha.names.${entity}`))}`;
const gardenEntities = computed(() => [
  entityId('binary_sensor', t('ha.names.garden'), 'watering_alert'),
  entityId('sensor', t('ha.names.garden'), 'items_to_water'),
  entityId('sensor', t('ha.names.garden'), 'total_plants'),
  entityId('button', t('ha.names.garden'), 'water_all'),
]);
const seedlingEntities = computed(() => [
  entityId('sensor', t('ha.names.seedlings'), 'seedling_total'),
  entityId('sensor', t('ha.names.seedlings'), 'seedling_varieties'),
]);
const haDevices = computed(() => [
  ...plots.value.filter(p => p.type === 'bed').map(p => ({ kind: 'bed', key: 'bed' + p.id, name: p.name || `Bed ${p.id}`, thirsty: bedNeedsWater(p) })),
  ...pots.value.map(p => ({ kind: 'pot', key: 'pot' + p.id, name: p.name || `Pot ${p.id}`, thirsty: potNeedsWater(p) })),
].map(d => ({
  ...d,
  entities: [
    entityId('binary_sensor', d.name, 'needs_water'),
    entityId('button', d.name, 'mark_watered'),
    entityId('sensor', d.name, 'last_watered'),
    ...(d.kind === 'bed' ? [entityId('sensor', d.name, 'plants')] : []),
  ],
})));

const haExamples = computed(() => {
  const bed = haDevices.value.find(d => d.kind === 'bed') || { name: t('ha.example_bed'), entities: [] };
  const id = slug(bed.name);
  const alert = gardenEntities.value[0];
  return [
    {
      key: 'ex-valve',
      title: t('ha.example_valve.title'),
      desc: t('ha.example_valve.desc'),
      yaml: `alias: "${t('ha.example_valve.alias', { name: bed.name })}"
trigger:
  - platform: time
    at: "21:00:00"
condition:
  - condition: state
    entity_id: ${entityId('binary_sensor', bed.name, 'needs_water')}
    state: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.valve_${id}
  - delay: "00:10:00"
  - service: switch.turn_off
    target:
      entity_id: switch.valve_${id}
  - service: button.press
    target:
      entity_id: ${entityId('button', bed.name, 'mark_watered')}`,
    },
    {
      key: 'ex-notify',
      title: t('ha.example_notify.title'),
      desc: t('ha.example_notify.desc'),
      yaml: `alias: "${t('ha.example_notify.alias')}"
trigger:
  - platform: state
    entity_id: ${alert}
    to: "on"
action:
  - service: notify.notify
    data:
      title: "My Secret Garden"
      message: >-
        ${t('ha.example_notify.message')} {{ (state_attr('${alert}', 'beds_to_water')
        + state_attr('${alert}', 'pots_to_water')) | join(', ') }}`,
    },
  ];
});

// Keep the browser tab icon in sync with the brand
onMounted(() => {
  let link = document.querySelector("link[rel~='icon']");
  if (!link) { link = document.createElement('link'); link.rel = 'icon'; document.head.appendChild(link); }
  link.href = 'data:image/svg+xml,' + encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🍑</text></svg>");
});
</script>
