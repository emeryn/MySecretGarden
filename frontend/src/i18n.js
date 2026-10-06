import { ref } from 'vue';
import en from './locales/en.js';
import fr from './locales/fr.js';

export const LOCALES = ['en', 'fr'];
const MESSAGES = { en, fr };
const STORAGE_KEY = 'msg_language';

function initialLocale() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (LOCALES.includes(saved)) return saved;
  } catch (e) {}
  return (navigator.language || '').toLowerCase().startsWith('fr') ? 'fr' : 'en';
}

export const locale = ref(initialLocale());
document.documentElement.lang = locale.value;

export function setLocale(value) {
  if (!LOCALES.includes(value)) return;
  locale.value = value;
  document.documentElement.lang = value;
  try { localStorage.setItem(STORAGE_KEY, value); } catch (e) {}
}

function lookup(messages, key) {
  return key.split('.').reduce((node, part) => (node == null ? undefined : node[part]), messages);
}

/**
 * Translate a key like "seeds.title". `{name}` placeholders are replaced by params.
 * Falls back to English, then to `fallback`, then to the key itself.
 */
export function t(key, params = {}, fallback) {
  let text = lookup(MESSAGES[locale.value], key);
  if (typeof text !== 'string') text = lookup(MESSAGES.en, key);
  if (typeof text !== 'string') return fallback ?? key;
  return text.replace(/\{(\w+)\}/g, (match, name) => (name in params ? params[name] : match));
}
