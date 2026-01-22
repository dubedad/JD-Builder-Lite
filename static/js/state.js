// Proxy-based reactive state management with localStorage persistence
const STORAGE_KEY = 'jdBuilderState';

const createStore = (initialState) => {
    const listeners = new Set();
    let state = initialState;

    // Helper to notify all listeners and persist
    const notify = () => {
        listeners.forEach(fn => fn(state));
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (e) {
            console.warn('localStorage save failed:', e);
        }
    };

    return {
        getState: () => state,
        subscribe: (fn) => {
            listeners.add(fn);
            return () => listeners.delete(fn);
        },
        // Update state and notify listeners
        setState: (updates) => {
            state = { ...state, ...updates };
            notify();
        },
        // Update selections specifically (common operation)
        setSelections: (sectionId, newSelections) => {
            state = {
                ...state,
                selections: {
                    ...state.selections,
                    [sectionId]: newSelections
                }
            };
            notify();
        },
        // Manually trigger notification (for complex updates)
        notify
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
        store.setState({
            selections: {
                key_activities: [],
                skills: [],
                effort: [],
                responsibility: [],
                working_conditions: []
            },
            currentProfileCode: nocCode
        });
    }
};

// Export for other modules
window.store = store;
window.resetSelectionsForProfile = resetSelectionsForProfile;
