import { createApp } from 'vue'
import App from './App.vue'
import VChart from 'vue-echarts'
import "./styles/ui.css";

const app = createApp(App)
app.component('VChart', VChart)
app.mount('#app')