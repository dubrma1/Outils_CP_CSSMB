/**
 * storage.js — Gestion de la persistance locale pour le suivi de stage (localStorage)
 * Conçu pour les enseignants : gestion des tâches complétées, personnalisation/exclusions et notes.
 * Respect strict des règles du projet : pas de classes, fonctions pures ES Modules.
 */

const STORAGE_PREFIX = 'fms_stage';

/**
 * Construit une clé de stockage pour un métier
 * @param {string} metierId 
 * @param {string} keyType 
 * @returns {string}
 */
function getStorageKey(metierId, keyType) {
  return `${STORAGE_PREFIX}:${metierId}:${keyType}`;
}

/**
 * Récupère un élément JSON du localStorage en toute sécurité
 * @param {string} key 
 * @param {*} defaultValue 
 * @returns {*}
 */
function getStoredJson(key, defaultValue) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return defaultValue;
    return JSON.parse(raw);
  } catch (err) {
    console.warn(`Lecture impossible pour la clé ${key}:`, err);
    return defaultValue;
  }
}

/**
 * Enregistre un élément en JSON dans le localStorage
 * @param {string} key 
 * @param {*} value 
 * @returns {boolean}
 */
function setStoredJson(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (err) {
    console.error(`Écriture impossible pour la clé ${key}:`, err);
    return false;
  }
}

/**
 * Charge les tâches complétées pour un métier donné
 * @param {string|number} metierId 
 * @returns {string[]}
 */
export function loadProgress(metierId) {
  if (!metierId) return [];
  const key = getStorageKey(String(metierId), 'tasks');
  const result = getStoredJson(key, []);
  return Array.isArray(result) ? result.map(String) : [];
}

/**
 * Sauvegarde la liste des tâches complétées
 * @param {string|number} metierId 
 * @param {Array<string|number>} taskIds 
 * @returns {boolean}
 */
export function saveProgress(metierId, taskIds) {
  if (!metierId) return false;
  const key = getStorageKey(String(metierId), 'tasks');
  const validList = Array.isArray(taskIds) ? taskIds.map(String) : [];
  return setStoredJson(key, validList);
}

/**
 * Bascule l'état complété d'une tâche
 * @param {string|number} metierId 
 * @param {string|number} taskId 
 * @returns {string[]} Nouvelle liste
 */
export function toggleTask(metierId, taskId) {
  const current = loadProgress(metierId);
  const idStr = String(taskId);
  const exists = current.includes(idStr);
  const updated = exists ? current.filter((id) => id !== idStr) : [...current, idStr];
  saveProgress(metierId, updated);
  return updated;
}

/**
 * Charge les exclusions d'une fiche personnalisée par l'enseignant
 * (compétences, tâches ou critères retirés du plan de formation)
 * @param {string|number} metierId 
 * @returns {{ comps: string[], tasks: string[], criteria: string[] }}
 */
export function loadExclusions(metierId) {
  if (!metierId) return { comps: [], tasks: [], criteria: [] };
  const key = getStorageKey(String(metierId), 'exclusions');
  const res = getStoredJson(key, { comps: [], tasks: [], criteria: [] });
  return {
    comps: Array.isArray(res.comps) ? res.comps.map(String) : [],
    tasks: Array.isArray(res.tasks) ? res.tasks.map(String) : [],
    criteria: Array.isArray(res.criteria) ? res.criteria.map(String) : []
  };
}

/**
 * Sauvegarde les exclusions
 * @param {string|number} metierId 
 * @param {{ comps: string[], tasks: string[], criteria: string[] }} exclusions 
 * @returns {boolean}
 */
export function saveExclusions(metierId, exclusions) {
  if (!metierId) return false;
  const key = getStorageKey(String(metierId), 'exclusions');
  return setStoredJson(key, {
    comps: Array.isArray(exclusions.comps) ? exclusions.comps.map(String) : [],
    tasks: Array.isArray(exclusions.tasks) ? exclusions.tasks.map(String) : [],
    criteria: Array.isArray(exclusions.criteria) ? exclusions.criteria.map(String) : []
  });
}

/**
 * Exclut un élément de la fiche personnalisée
 * @param {string|number} metierId 
 * @param {'comps'|'tasks'|'criteria'} type 
 * @param {string} id 
 * @returns {{ comps: string[], tasks: string[], criteria: string[] }}
 */
export function excludeItem(metierId, type, id) {
  const current = loadExclusions(metierId);
  const idStr = String(id);
  if (!current[type].includes(idStr)) {
    current[type].push(idStr);
    saveExclusions(metierId, current);
  }
  return current;
}

/**
 * Restaure un élément précédemment exclu de la fiche
 * @param {string|number} metierId 
 * @param {'comps'|'tasks'|'criteria'} type 
 * @param {string} id 
 * @returns {{ comps: string[], tasks: string[], criteria: string[] }}
 */
export function restoreItem(metierId, type, id) {
  const current = loadExclusions(metierId);
  const idStr = String(id);
  current[type] = current[type].filter((item) => item !== idStr);
  saveExclusions(metierId, current);
  return current;
}

/**
 * Réinitialise toutes les exclusions pour rétablir la fiche officielle standard
 * @param {string|number} metierId 
 * @returns {boolean}
 */
export function resetExclusions(metierId) {
  if (!metierId) return false;
  const key = getStorageKey(String(metierId), 'exclusions');
  try {
    localStorage.removeItem(key);
    return true;
  } catch (err) {
    return false;
  }
}

/**
 * Charge les informations de stage (Nom de l'élève, superviseur, école)
 * @param {string|number} metierId 
 * @returns {Object}
 */
export function loadStageInfo(metierId) {
  if (!metierId) return { eleveNom: '', milieuStage: '', enseignantNom: '', dateDebut: '' };
  const key = getStorageKey(String(metierId), 'info');
  return getStoredJson(key, { eleveNom: '', milieuStage: '', enseignantNom: '', dateDebut: '' });
}

/**
 * Sauvegarde les informations de stage
 * @param {string|number} metierId 
 * @param {Object} info 
 * @returns {boolean}
 */
export function saveStageInfo(metierId, info) {
  if (!metierId) return false;
  const key = getStorageKey(String(metierId), 'info');
  return setStoredJson(key, info);
}

/**
 * Réinitialise complètement le suivi d'un métier (action destructive confirmée par l'enseignant)
 * @param {string|number} metierId 
 * @returns {boolean}
 */
export function resetStageTracking(metierId) {
  if (!metierId) return false;
  const mid = String(metierId);
  try {
    localStorage.removeItem(getStorageKey(mid, 'tasks'));
    localStorage.removeItem(getStorageKey(mid, 'info'));
    // Remarque : on peut choisir de conserver ou effacer les exclusions lors du reset complet
    return true;
  } catch (err) {
    console.error(`Erreur réinitialisation pour le métier ${mid}:`, err);
    return false;
  }
}
