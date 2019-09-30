package main

import (
  "bufio"
  "fmt"
  "os"
)

func check(e error) {
    if e != nil {
        panic(e)
    }
}

func main () {
  vertsFilename := "../input/verts-with-simplified.txt"
  edgesFilename := "../input/edges-cleaned.txt"
  vertsFile, err := os.Open(vertsFilename)
  check(err)

  vertsScanner := bufio.NewScanner(vertsFile)
  vertsScanner.Split(bufio.ScanLines)

  i := 0
  for vertsScanner.Scan() {
    i += 1
  }

  fmt.Print(i)

  edgesFile, err := os.Open(edgesFilename)
  check(err)
  
  edgesScanner := bufio.NewScanner(edgesFile)
  edgesScanner.Split(bufio.ScanLines)

  for edgesScanner.Scan() {

  }

}
