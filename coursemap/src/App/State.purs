module App.State where

import Prelude

import App.Config (config)
import App.Routes (Route, match)
import Data.Newtype (class Newtype)
import Data.Tuple (Tuple(..))
import Signal.DOM (DimensionPair)

type State =
  { rings :: Array Ring
  , screenDim :: ScreenDim
  , routing :: RoutingState
  }

type ScreenDim = DimensionPair

type Ring =
  { plans :: Array Plan
  , interval :: Interval
  }

-- instance eqRing :: (Ord Ring) where
--   eq a b = eq a.interval b.interval
--
-- instance ordRing :: (Ord Ring) where
--   compare a b = compare a.interval b.interval

type Plan = String
type Interval = String

type RoutingState =
  { title :: String
  , route :: Route
  , loaded :: Boolean
  }

init :: String -> State
init url =
  { rings: testRings,
    screenDim: {w: 0, h: 0},
    routing:
      { title: config.title
      , route: match url
      , loaded: false
      }
  }

testRings =
  [ {interval: "1 day", plans: ["get milk", "comb beard"]}
  , {interval: "1 year", plans: ["publish studypath", "make plant group sustainable"] }]
