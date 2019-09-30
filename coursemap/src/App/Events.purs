module App.Events where

import App.Routes (Route)
import App.State (State)
import Data.Function (($))
import Data.Tuple (Tuple(..))
import Debug.Trace (spy)
import Network.HTTP.Affjax (AJAX)
import Pux (EffModel, noEffects)
import Signal.DOM (DimensionPair)

data Event
  = PageView Route
  | ResizeWindow DimensionPair

type AppEffects fx = (ajax :: AJAX | fx)

foldp :: ∀ fx. Event -> State -> EffModel State Event (AppEffects fx)
foldp (PageView route) st = noEffects $ st { routing = st.routing {route = route, loaded = true }}
foldp (ResizeWindow dim) st =
  noEffects $ st { screenDim = dim }
