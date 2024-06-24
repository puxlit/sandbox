package main

import (
	"fmt"
	"math/rand"
	"time"
)

type card struct {
	value string
	suit  string
}

func (c *card) String() string {
	return fmt.Sprintf("%s%s", c.value, c.suit)
}

var cardValues = []string{"2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"}
var cardSuits = []string{"h", "c", "d", "s"}
var handSize = 12
var requiredWins = 5
var margin = 10
var winsToFind = requiredWins + margin

func randHand(r rand.Rand) []card {
	hand := make([]card, handSize)
	sum := 0
	for sum < handSize {
		hand[sum] = card{
			value: cardValues[r.Intn(len(cardValues))],
			suit:  cardSuits[r.Intn(len(cardSuits))],
		}
		sum++
	}
	return hand
}

func isFiveOfAKind(hand []card) bool {
	counts := make(map[string]int)
	for _, card := range hand {
		element := card.value
		counts[element] = counts[element] + 1
		if counts[element] >= 5 {
			return true
		}
	}
	return false
}

func main() {
	timeNow := time.Now().UTC().Unix()
	fmt.Printf("t = %v (%v)\n", timeNow, time.Unix(timeNow, 0).Format(time.RFC3339))

	for i, winsFound := int64(0), 0; winsFound < winsToFind; i++ {
		timeSeed := timeNow + i
		r := rand.New(rand.NewSource(timeSeed))
		hand := randHand(*r)

		if !isFiveOfAKind(hand) {
			continue
		}

		winsFound++
		fmt.Printf("Win %v at t = %v (%v): %v\n", winsFound, timeSeed, time.Unix(timeSeed, 0).Format(time.RFC3339), hand)
	}
}
