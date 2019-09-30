package main

import (
  "fmt"
  "strings"
  "strconv"
)

func main () {
  fmt.Println("HI")
  fmt.Println(strconv.Atoi("23"))
  fmt.Println(strconv.Itoa(23))
  fmt.Println(strings.ToLower("HIhi"))
  ss := strings.Split("hi\tthere", "\t")
  fmt.Print(ss[1])
}
