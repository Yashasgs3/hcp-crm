import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE = '/api/interactions';

export const sendChatMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ message, interactionId, extractedData }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message,
        interaction_id: interactionId,
        extracted_data: extractedData,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to send message.'
      );
    }
  }
);

const initialState = {
  messages: [],
  loading: false,
  error: null,
  lastToolResult: null,
  lastIntent: null,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({
        id: Date.now(),
        role: 'user',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    addAssistantMessage: (state, action) => {
      state.messages.push({
        id: Date.now() + 1,
        role: 'assistant',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    clearChat: (state) => {
      state.messages = [];
      state.lastToolResult = null;
      state.lastIntent = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false;
        const { intent, tool_result, response } = action.payload;
        state.lastIntent = intent;
        state.lastToolResult = tool_result;
        if (response) {
          state.messages.push({
            id: Date.now() + 1,
            role: 'assistant',
            content: response,
            toolResult: tool_result,
            intent: intent,
            timestamp: new Date().toISOString(),
          });
        }
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'An error occurred.';
        state.messages.push({
          id: Date.now() + 1,
          role: 'assistant',
          content: `Error: ${action.payload || 'Something went wrong.'}`,
          timestamp: new Date().toISOString(),
          isError: true,
        });
      });
  },
});

export const { addUserMessage, addAssistantMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
