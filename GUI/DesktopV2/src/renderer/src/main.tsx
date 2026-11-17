/* @refresh reload */
import { render } from 'solid-js/web'
import { App } from './App'
import './styles/main.css'

const root = document.getElementById('root')

if (!root) {
  throw new Error('Root container #root not found in index.html')
}

render(() => <App />, root)
