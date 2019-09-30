module App.View.Homepage where

import Prelude
import Text.Smolder.SVG
import Text.Smolder.SVG.Attributes

import App.Events (Event)
import App.State (State)
import Control.Bind (discard)
import Data.Array (length, range, sortBy, zip)
import Data.Function (($))
import Data.Traversable (for_)
import Data.Tuple (Tuple(..))
import Debug.Trace
import Pux.DOM.HTML (HTML)
import Text.Smolder.Markup ((!), text)

view :: State -> HTML Event
view s =
  svg ! width "100%" ! height "100%" $ do
    g ! transform translation $ for_ (zip (range 0 numRings) rings) $ \(Tuple i ring) ->
      let radius = show ((i + 1) * 100) <> "px"
      in circle ! r radius ! cx "0" ! cy "0" ! stroke "white" ! fill "none"
  where
    {w, h} = s.screenDim
    translation = "translate(" <> show (w / 2) <> "," <> show h <> ")"
    rings = sortBy (comparing _.interval) s.rings
    numRings = length rings
