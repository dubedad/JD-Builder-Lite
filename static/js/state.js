// Proxy-based reactive state management with localStorage persistence
const STORAGE_KEY = 'jdBuilderState';

const createStore = (initialState) => {
    const listeners = new Set();

    const handler = {
        set(target, key, value) {
            target[key] = value;
            listeners.forEach(fn => fn(target));
            // Persist to localStorage
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(target));
            } catch (e) {
                console.warn('localStorage save failed:', e);
            }
            return true;
        }
    };

    const state = new Proxy(initialState, handler);

    return {
        getState: () => state,
        subscribe: (fn) => {
            listeners.add(fn);
            return () => listeners.delete(fn);
        },
        // Batch update without multiple notifications
        batch: (updates) => {
            Object.assign(state, updates);
        }
    };
};

// Load persisted state or use defaults
const loadPersistedState = () => {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            return JSON.parse(saved);
        }
    } catch (e) {
        console.warn('localStorage load failed:', e);
    }
    return null;
};

const defaultState = {
    selections: {
        key_activities: [],
        skills: [],
        effort: [],
        responsibility: [],
        working_conditions: []
    },
    sectionOrder: ['key_activities', 'skills', 'effort', 'responsibility', 'working_conditions'],
    currentProfileCode: null
};

const persistedState = loadPersistedState();
const initialState = persistedState || defaultState;

// Create the store
const store = createStore(initialState);

// Reset selections when profile changes
const resetSelectionsForProfile = (nocCode) => {
    const state = store.getState();
    if (state.currentProfileCode !== nocCode) {
        state.selections = {
            key_activities: [],
            skills: [],
            effort: [],
            responsibility: [],
            working_conditions: []
        };
        state.currentProfileCode = nocCode;
    }
};

// Export for other modules
window.store = store;
window.resetSelectionsForProfile = resetSelectionsForProfile;
