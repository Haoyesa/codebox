import { ref, readonly } from 'vue';

const STORAGE_KEY = 'fulltool_settings_v2';

const defaultSettings = {
  loDir: '',
  outputDir: '',
  authKey: '',
  lastVerify: '',
  nextCheck: ''
};

const settings = ref({ ...defaultSettings });

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      settings.value = { ...defaultSettings, ...parsed };
    }
  } catch (_) {}
}

function save() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value));
  } catch (_) {}
}

function set(key, value) {
  settings.value[key] = value;
  save();
}

function get(key) {
  return settings.value[key];
}

function reset() {
  settings.value = { ...defaultSettings };
  save();
}

// Load immediately
load();

export function useSettings() {
  return {
    settings: readonly(settings),
    set,
    get,
    save,
    reset,
    load
  };
}
