// Reference gardening data. Plant names exist in both languages so companion planting
// is detected whatever language the user typed the variety name in.

export const CATEGORIES = ['fruit_vegetable', 'root_vegetable', 'leaf_vegetable', 'companion_flower', 'bulb', 'herb', 'cereal'];
export const SOILS = ['clay', 'sandy', 'loamy', 'humus', 'chalky', 'any'];
export const WATERING_INTERVALS = [1, 2, 3, 7, 14, 30];
export const TREE_SIZES = ['small', 'medium', 'large'];

export const SEED_ICONS = ['🌱', '🌿', '🍅', '🥕', '🥔', '🥬', '🧅', '🧄', '🥦', '🥒', '🍆', '🌶️', '🌽', '🍓', '🍈', '🍉', '🎃', '🌼', '🌻', '🪻'];
export const DECOR_ICONS = ['🪑', '🪣', '🦆', '🦔', '🐝', '🐌', '🦉', '🦋', '🐈', '🐸', '🪵', '⛲', '🪨', '🍄', '🛒', '🚲'];
export const POT_ICONS = ['🪴', '🌵', '🌴', '🌲', '🌳', '🌿', '☘️', '🍀', '🍃', '🌸', '🌼', '🪻', '🌻', '🌺', '🌹', '🌾', '🍋', '🍅', '🌶️'];

// code: [English name, French name, ...other spellings used for matching]
export const PLANTS = {
  wormwood: ['Wormwood', 'Absinthe'],
  garlic: ['Garlic', 'Ail'],
  amaranth: ['Amaranth', 'Amaranthe'],
  dill: ['Dill', 'Aneth'],
  artichoke: ['Artichoke', 'Artichaut'],
  asparagus: ['Asparagus', 'Asperge'],
  eggplant: ['Eggplant', 'Aubergine', 'Aubergine'],
  basil: ['Basil', 'Basilic'],
  chard: ['Chard', 'Bette', 'Blette'],
  beetroot: ['Beetroot', 'Betterave', 'Beet'],
  borage: ['Borage', 'Bourrache'],
  calendula: ['Calendula', 'Calendula'],
  chamomile: ['Chamomile', 'Camomille'],
  nasturtium: ['Nasturtium', 'Capucine'],
  cardoon: ['Cardoon', 'Cardon'],
  carrot: ['Carrot', 'Carotte'],
  caraway: ['Caraway', 'Carvi'],
  celery: ['Celery', 'Céleri'],
  celeriac: ['Celeriac', 'Céleri-rave'],
  chervil: ['Chervil', 'Cerfeuil'],
  chicory: ['Chicory', 'Chicorée', 'Endive'],
  cabbage: ['Cabbage', 'Chou'],
  brussels_sprouts: ['Brussels sprouts', 'Chou de Bruxelles'],
  cauliflower: ['Cauliflower', 'Chou-fleur'],
  kohlrabi: ['Kohlrabi', 'Chou-rave'],
  chives: ['Chives', 'Ciboulette'],
  cucumber: ['Cucumber', 'Concombre'],
  coriander: ['Coriander', 'Coriandre', 'Cilantro'],
  gherkin: ['Gherkin', 'Cornichon'],
  cosmos: ['Cosmos', 'Cosmos'],
  squash: ['Squash', 'Courge'],
  zucchini: ['Zucchini', 'Courgette', 'Courgette'],
  watercress: ['Watercress', 'Cresson'],
  shallot: ['Shallot', 'Échalote', 'Échalotte'],
  spinach: ['Spinach', 'Épinard'],
  tarragon: ['Tarragon', 'Estragon'],
  fennel: ['Fennel', 'Fenouil'],
  broad_bean: ['Broad bean', 'Fève', 'Fava bean'],
  strawberry: ['Strawberry', 'Fraise', 'Fraisier'],
  geranium: ['Geranium', 'Géranium'],
  bean: ['Bean', 'Haricot'],
  shelling_bean: ['Shelling bean', 'Haricot en grain'],
  carnation: ['Carnation', 'Œillet', 'Oeillet', 'Marigold'],
  lettuce: ['Lettuce', 'Laitue', 'Salade', 'Salad'],
  flax: ['Flax', 'Lin'],
  lovage: ['Lovage', 'Livèche'],
  lambs_lettuce: ["Lamb's lettuce", 'Mâche', 'Corn salad'],
  corn: ['Corn', 'Maïs', 'Maize', 'Sweetcorn'],
  marjoram: ['Marjoram', 'Marjolaine'],
  melon: ['Melon', 'Melon'],
  mint: ['Mint', 'Menthe'],
  mustard: ['Mustard', 'Moutarde'],
  turnip: ['Turnip', 'Navet'],
  onion: ['Onion', 'Oignon'],
  oregano: ['Oregano', 'Origan'],
  parsnip: ['Parsnip', 'Panais'],
  watermelon: ['Watermelon', 'Pastèque'],
  sweet_potato: ['Sweet potato', 'Patate douce'],
  pattypan: ['Pattypan squash', 'Pâtisson'],
  parsley: ['Parsley', 'Persil'],
  chili: ['Chili pepper', 'Piment'],
  leek: ['Leek', 'Poireau'],
  pea: ['Pea', 'Pois'],
  pepper: ['Bell pepper', 'Poivron', 'Sweet pepper'],
  potato: ['Potato', 'Pomme de terre'],
  pumpkin: ['Pumpkin', 'Potiron'],
  radish: ['Radish', 'Radis'],
  horseradish: ['Horseradish', 'Raifort'],
  castor_bean: ['Castor bean', 'Ricin'],
  rosemary: ['Rosemary', 'Romarin'],
  arugula: ['Arugula', 'Roquette', 'Rocket'],
  rose: ['Rose', 'Rosier'],
  rue: ['Rue', 'Rue'],
  salsify: ['Salsify', 'Salsifis'],
  savory: ['Savory', 'Sarriette'],
  sage: ['Sage', 'Sauge'],
  pot_marigold: ['Pot marigold', 'Souci'],
  tansy: ['Tansy', 'Tanaisie'],
  nz_spinach: ['New Zealand spinach', 'Tétragone'],
  thyme: ['Thyme', 'Thym'],
  tomato: ['Tomato', 'Tomate'],
  sunflower: ['Sunflower', 'Tournesol'],
  grapevine: ['Grapevine', 'Vigne'],
};

export const COMPANIONS = [
  { plant: 'garlic', good: ['beetroot', 'carrot', 'cabbage', 'strawberry', 'lettuce', 'tomato'], bad: ['asparagus', 'bean', 'parsley', 'pea', 'leek', 'potato'] },
  { plant: 'eggplant', good: ['garlic', 'calendula', 'tarragon', 'bean', 'lettuce', 'mint', 'onion', 'parsley', 'chili', 'pea', 'pot_marigold', 'thyme', 'tomato'], bad: ['potato'] },
  { plant: 'basil', good: ['pepper', 'tomato', 'cucumber', 'gherkin', 'squash', 'melon', 'cabbage', 'broad_bean', 'zucchini', 'fennel', 'asparagus'], bad: ['rue', 'wormwood'] },
  { plant: 'chard', good: ['onion'], bad: ['carrot'] },
  { plant: 'beetroot', good: ['celery', 'cabbage', 'cauliflower', 'kohlrabi', 'lettuce', 'onion', 'radish'], bad: ['asparagus', 'carrot', 'bean', 'tomato'] },
  { plant: 'carrot', good: ['beetroot', 'coriander', 'pea', 'lettuce', 'arugula', 'parsnip', 'salsify', 'pepper', 'flax', 'parsley', 'leek', 'sage', 'tomato', 'radish', 'garlic', 'chives', 'shallot', 'onion'], bad: ['strawberry', 'mint', 'corn', 'chard'] },
  { plant: 'celery', good: ['leek', 'cabbage'], bad: ['carrot', 'corn', 'parsley'] },
  { plant: 'chervil', good: ['radish', 'lettuce', 'cauliflower', 'chicory'], bad: [] },
  { plant: 'chicory', good: ['spinach', 'arugula', 'pot_marigold', 'chervil'], bad: ['brussels_sprouts', 'asparagus', 'turnip'] },
  { plant: 'cabbage', good: ['dill', 'beetroot', 'celery', 'spinach', 'lettuce', 'bean', 'rosemary', 'sage', 'chamomile', 'geranium', 'mint', 'potato'], bad: ['shallot', 'fennel', 'strawberry', 'shelling_bean', 'pattypan', 'leek', 'pepper', 'radish', 'tomato', 'grapevine'] },
  { plant: 'coriander', good: ['beetroot', 'carrot', 'cucumber', 'cabbage', 'potato'], bad: ['fennel', 'sage'] },
  { plant: 'cucumber', good: ['dill', 'bean', 'lettuce', 'corn', 'onion', 'basil'], bad: ['melon', 'potato', 'tomato', 'horseradish'] },
  { plant: 'squash', good: ['asparagus', 'celery', 'cabbage', 'lettuce', 'lambs_lettuce', 'pea', 'onion', 'basil', 'chives', 'coriander', 'oregano', 'nasturtium', 'tansy', 'sunflower'], bad: ['radish', 'fennel'] },
  { plant: 'zucchini', good: ['asparagus', 'celery', 'cabbage', 'lettuce', 'lambs_lettuce', 'pea', 'onion', 'basil', 'chives', 'coriander', 'oregano', 'nasturtium', 'tansy', 'sunflower'], bad: ['radish', 'fennel'] },
  { plant: 'spinach', good: ['eggplant', 'cabbage', 'artichoke', 'chicory', 'strawberry', 'broad_bean', 'bean', 'pea', 'lettuce', 'onion', 'leek', 'radish', 'thyme'], bad: ['chard', 'beetroot', 'potato', 'tomato', 'pepper'] },
  { plant: 'fennel', good: ['celeriac', 'leek', 'basil'], bad: ['tomato', 'wormwood', 'cucumber', 'pepper', 'spinach', 'bean', 'squash', 'pot_marigold', 'turnip', 'cabbage', 'coriander', 'caraway'] },
  { plant: 'broad_bean', good: ['carrot', 'celery', 'cabbage', 'corn', 'lettuce', 'savory', 'basil'], bad: ['garlic', 'beetroot', 'onion', 'leek', 'potato'] },
  { plant: 'strawberry', good: ['leek', 'thyme'], bad: ['cabbage'] },
  { plant: 'bean', good: ['corn', 'pumpkin', 'cabbage', 'melon', 'watermelon', 'carrot', 'celery', 'cucumber', 'potato', 'spinach', 'lettuce', 'borage', 'nasturtium', 'savory', 'sunflower', 'wormwood'], bad: ['leek', 'garlic', 'shallot', 'onion', 'chives', 'fennel', 'pea', 'zucchini'] },
  { plant: 'lettuce', good: ['cabbage', 'carrot', 'onion', 'cardoon', 'pea', 'beetroot', 'chard', 'squash', 'broad_bean', 'strawberry', 'melon', 'bean', 'turnip', 'leek', 'artichoke', 'chervil', 'dill', 'flax'], bad: ['corn', 'parsnip'] },
  { plant: 'lambs_lettuce', good: ['cabbage', 'onion', 'leek'], bad: ['amaranth'] },
  { plant: 'corn', good: ['beetroot', 'bean', 'pea', 'pumpkin', 'sunflower'], bad: ['lettuce', 'onion'] },
  { plant: 'melon', good: ['lettuce', 'basil', 'bean', 'watermelon'], bad: ['cucumber'] },
  { plant: 'turnip', good: ['lettuce', 'mint', 'pea', 'rosemary'], bad: ['garlic'] },
  { plant: 'onion', good: ['beetroot', 'chamomile', 'carrot', 'fennel', 'strawberry', 'lettuce', 'lambs_lettuce', 'radish', 'tomato', 'potato'], bad: ['cabbage', 'broad_bean', 'bean', 'corn', 'parsley', 'leek', 'pea'] },
  { plant: 'parsnip', good: ['radish', 'beetroot', 'kohlrabi', 'onion'], bad: ['dill', 'lettuce'] },
  { plant: 'parsley', good: ['radish', 'tomato', 'rose', 'artichoke', 'asparagus'], bad: ['celery', 'pea', 'lettuce', 'leek'] },
  { plant: 'chili', good: ['basil', 'carrot', 'lovage', 'marjoram', 'tomato', 'eggplant', 'onion'], bad: ['fennel', 'kohlrabi', 'sweet_potato', 'bean'] },
  { plant: 'pepper', good: ['basil', 'carrot', 'lovage', 'marjoram', 'tomato', 'eggplant', 'onion'], bad: ['fennel', 'kohlrabi', 'sweet_potato', 'bean'] },
  { plant: 'potato', good: ['borage', 'cabbage', 'coriander', 'shallot', 'broad_bean', 'bean', 'lettuce', 'carnation', 'pea', 'radish', 'pot_marigold'], bad: ['sunflower', 'corn', 'garlic', 'onion'] },
  { plant: 'leek', good: ['carrot', 'celery', 'strawberry', 'tomato', 'asparagus', 'lettuce', 'lambs_lettuce', 'fennel', 'artichoke', 'mustard', 'watercress'], bad: ['chard', 'beetroot', 'cabbage', 'bean', 'parsley', 'pea'] },
  { plant: 'pea', good: ['potato', 'coriander', 'castor_bean', 'cabbage', 'celery', 'carrot', 'asparagus', 'lettuce', 'radish', 'bean', 'corn', 'turnip', 'squash', 'cucumber', 'sunflower', 'caraway', 'savory'], bad: ['garlic', 'shallot', 'onion', 'parsley', 'leek', 'chives'] },
  { plant: 'radish', good: ['watercress', 'chervil', 'parsnip', 'carrot', 'pea', 'cucumber', 'gherkin', 'spinach', 'bean', 'celeriac', 'potato', 'tomato', 'onion'], bad: ['cabbage', 'chives', 'zucchini', 'sunflower', 'savory'] },
  { plant: 'tomato', good: ['dill', 'basil', 'parsley', 'carrot', 'celery', 'cosmos', 'chamomile', 'cabbage', 'carnation', 'watermelon', 'cucumber', 'radish', 'nz_spinach', 'nasturtium', 'corn'], bad: ['fennel', 'sunflower', 'beetroot', 'chard', 'pea', 'kohlrabi'] },
];

export const ROTATION = [
  { id: 'legumes', plants: ['broad_bean', 'bean', 'pea'] },
  { id: 'leaves', plants: ['basil', 'chard', 'celery', 'chervil', 'chicory', 'cabbage', 'coriander', 'spinach', 'fennel', 'lettuce', 'lambs_lettuce', 'parsley', 'leek'] },
  { id: 'roots', plants: ['garlic', 'beetroot', 'carrot', 'turnip', 'onion', 'parsnip', 'potato', 'radish'] },
  { id: 'fruits', plants: ['eggplant', 'cucumber', 'squash', 'zucchini', 'strawberry', 'corn', 'melon', 'chili', 'pepper', 'tomato'] },
];

// Rows of the "needs by family" table: translation keys live under reference.needs.<id>
export const FAMILY_NEEDS = [
  { id: 'nightshades', family: 'fruits' },
  { id: 'cucurbits', family: 'fruits' },
  { id: 'strawberry', family: 'fruits' },
  { id: 'salads', family: 'leaves' },
  { id: 'brassicas', family: 'leaves' },
  { id: 'herbs', family: 'leaves' },
  { id: 'carrots', family: 'roots' },
  { id: 'radishes', family: 'roots' },
  { id: 'alliums', family: 'roots' },
  { id: 'potato', family: 'roots' },
  { id: 'legumes', family: 'legumes' },
];

export const SOIL_TIPS = [
  { id: 'spring', icon: '🌱' },
  { id: 'summer', icon: '☀️' },
  { id: 'autumn', icon: '🍂' },
  { id: 'winter', icon: '❄️' },
];

const normalize = (text) => (text || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/œ/g, 'oe').trim();

/** Display name of a plant code in the given language. */
export function plantName(code, locale) {
  const names = PLANTS[code];
  if (!names) return code;
  return locale === 'fr' ? names[1] : names[0];
}

/**
 * Find the plant code matching a free-text variety name ("Tomate cœur de bœuf" → tomato).
 * Variety names start with the species, so the earliest match wins ("Ail rose" is garlic, not rose);
 * at the same position the longest wins ("Chou-fleur" is cauliflower, not cabbage).
 */
export function findPlant(varietyName) {
  const text = normalize(varietyName);
  if (!text) return null;
  let best = null;
  let bestPosition = Infinity;
  let bestLength = 0;
  for (const [code, names] of Object.entries(PLANTS)) {
    for (const name of names) {
      const n = normalize(name);
      // Whole word, plural allowed: "Tomates cerises" matches "tomate"
      const match = new RegExp(`(^|[^a-z])${n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(e?s|x)?(?=[^a-z]|$)`).exec(text);
      if (!match) continue;
      const position = match.index + match[1].length;
      if (position < bestPosition || (position === bestPosition && n.length > bestLength)) {
        best = code; bestPosition = position; bestLength = n.length;
      }
    }
  }
  return best;
}

/** Companion relationship between two varieties: { good, bad }. */
export function companionship(nameA, nameB) {
  const a = findPlant(nameA);
  const b = findPlant(nameB);
  if (!a || !b) return { good: false, bad: false };
  const entryA = COMPANIONS.find(c => c.plant === a);
  const entryB = COMPANIONS.find(c => c.plant === b);
  return {
    good: Boolean(entryA?.good.includes(b) || entryB?.good.includes(a)),
    bad: Boolean(entryA?.bad.includes(b) || entryB?.bad.includes(a)),
  };
}
