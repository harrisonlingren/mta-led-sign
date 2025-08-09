// MTA setup
require('dotenv').config()
const Mta = require('mta-gtfs-jl')
const mta = new Mta({
  key: process.env.API_KEY,
  feed_id: process.env.FEED_ID
})

// Express setup
const express = require('express')
const app = express()
const port = process.env.PORT || 8080
const router = express.Router()
app.use(express.json())

// helper function to identify feed
feeds = require('./feeds.json')
function getFeedForLine(line) {
  return feeds[line] || undefined
}

// middleware to use for all requests
router.use((req, res, next) => {
	next()
})

router.get('/', (req, res) => {
	res.json({ message: 'Welcome to the NYC Train Sign API'})
})

router.route('/status')
	.get(async (req, res ) => {
    const result = await mta.status('subway')
    res.send(result)
  })

router.route('/status/:id')
	.get(async (req, res ) => {
    const result = await mta.status('subway')
    const filteredResult = result.find(o => o.name.includes(req.params.id))
    res.send(filteredResult)
  })

router.route('/station')
  .get(async (req, res ) => {
    const result = await mta.stop()
    res.send(result)
  })

router.route('/station/:id')
	.get(async (req, res ) => {
    const result = await mta.stop(req.params.id)
    res.send(result)
  })

router.route('/schedule')
  .get(async (req, res ) => {
    res.json({ message: 'A station ID is required as a parameter to retrieve a schedule. Ex: /api/schedule/249'})
  })

router.route('/schedule/:id')
	.get(async (req, res ) => {
    try {
      const feed = getFeedForLine(req.params.trainName)
      const result = await mta.schedule(req.params.id, feed)
      if (result.schedule) {
        res.send(result.schedule[req.params.id])
      } else {
        throw new Error("Cound not fetch schedule for " + req.params.id);
      }
    } catch (error) {
      console.log(error);
      res.sendStatus(502);
    }
  })

router.route('/schedule/:id/:direction')
  .get(async (req, res ) => {
    try {
      const feedPrefix = req.params.id[0]
      const feed = getFeedForLine(feedPrefix)
      const direction = req.params.direction
      if (direction == "N" || direction == "S") {
        const result = await mta.schedule(req.params.id, feed)
        if (result.schedule) {
          result.schedule[req.params.id][direction].forEach(arrivalInfo => {
            arrivalInfo.relativeTime = timeToRelative(arrivalInfo.arrivalTime)
          })
          res.send(result.schedule[req.params.id][direction])
        } else {
          res.send([]);  // send empty list if no schedule
        }
      } else {
        res.sendStatus(400);
      }
    } catch (error) {
      console.log(error);
      res.sendStatus(502);
    }
  })

router.route('/schedule/:stationId/:lines/:direction')
  .get(async (req, res) => {
    try {
      const stationId = req.params.stationId;
      const lines = req.params.lines.split(',');
      const direction = req.params.direction;

      if (direction !== "N" && direction !== "S") {
        return res.sendStatus(400);
      }

      let combinedSchedule = [];
      const feedsToFetch = new Set(lines.map(line => getFeedForLine(line)).filter(feed => feed !== undefined));

      for (const feed of feedsToFetch) {
        const result = await mta.schedule(stationId, feed);
        if (result.schedule && result.schedule[stationId] && result.schedule[stationId][direction]) {
          result.schedule[stationId][direction].forEach(arrivalInfo => {
            if (lines.includes(arrivalInfo.routeId)) {
              arrivalInfo.relativeTime = timeToRelative(arrivalInfo.arrivalTime);
              combinedSchedule.push(arrivalInfo);
            }
          });
        }
      }

      combinedSchedule.sort((a, b) => a.arrivalTime - b.arrivalTime);

      if (combinedSchedule.length > 0) {
        res.send(combinedSchedule);
      } else {
        res.send([]); // send empty list if no schedule
      }
    } catch (error) {
      console.log(error);
      res.sendStatus(502);
    }
  });

const timeToRelative = (time) => {
  const now = new Date().valueOf()
  const diff = (time * 1000) - now
  const minsDiff = Math.floor(diff / 6e4);
  return minsDiff
}

// Register the routes & start the server
app.use('/api', router)
app.use('/config', express.static('config_page'))
app.listen(port, (err) => {
  if (err) return console.log(`Something bad happened: ${err}`)
  console.log(`Node.js server listening on ${port}`)
})