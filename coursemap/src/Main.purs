module Main where

import Prelude

import App.Events (AppEffects, Event(..), foldp)
import App.Routes (match)
import App.State (State, init)
import App.View.Layout (view)
import Control.Monad.Eff (Eff)
import DOM (DOM)
import DOM.HTML (window)
import DOM.HTML.Types (HISTORY)
import Data.Tuple (Tuple(..))
import Debug.Trace (spy)
import Pux (CoreEffects, App, start)
import Pux.DOM.Events (DOMEvent)
import Pux.DOM.History (sampleURL)
import Pux.Renderer.React (renderToDOM)
import Signal (constant, (~>))
import Signal.DOM (DimensionPair, windowDimensions)

type WebApp = App (DOMEvent -> Event) Event State

type ClientEffects = CoreEffects (AppEffects (history :: HISTORY, dom :: DOM))

main :: String -> DimensionPair -> State -> Eff ClientEffects WebApp
main url dims state = do
  -- | Create a signal of URL changes.
  urlSignal <- sampleURL =<< window
  -- | Map a signal of URL changes to PageView actions.
  let routeSignal = urlSignal ~> \r -> PageView (match r)

  winSig <- windowDimensions
  let resizeSignal = winSig ~> ResizeWindow

  -- | Start the app.
  app <- start
    { initialState: state { screenDim = dims }
    , view
    , foldp
    , inputs: [routeSignal, resizeSignal] }

  -- | Render to the DOM
  renderToDOM "#app-root" app.markup app.input

  -- | Return app to be used for hot reloading logic in support/client.entry.js
  pure app

initialState :: State
initialState = init "/"
