import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  interactionId: null,
  formData: {
    hcp_name: '',
    specialty: '',
    hospital: '',
    interaction_type: '',
    interaction_date: '',
    interaction_time: '',
    attendees: '',
    discussion_topics: '',
    products_discussed: '',
    objections: '',
    materials_shared: '',
    samples_given: '',
    sentiment: '',
    summary: '',
    follow_up_required: '',
    follow_up_date: '',
    next_action: '',
  },
  isFormPopulated: false,
  loading: false,
  error: null,
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    setInteractionId: (state, action) => {
      state.interactionId = action.payload;
    },
    updateFormData: (state, action) => {
      state.formData = { ...state.formData, ...action.payload };
      state.isFormPopulated = true;
    },
    setFormField: (state, action) => {
      const { field, value } = action.payload;
      state.formData[field] = value;
    },
    resetForm: (state) => {
      state.formData = initialState.formData;
      state.interactionId = null;
      state.isFormPopulated = false;
      state.error = null;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setInteractionId,
  updateFormData,
  setFormField,
  resetForm,
  setLoading,
  setError,
} = interactionSlice.actions;

export default interactionSlice.reducer;
