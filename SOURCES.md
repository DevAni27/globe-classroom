# Lesson evidence

Source links checked 26 October 2026. This is a prepared geography lesson, not live weather. No measured rainfall amounts or station observations are represented. Ring coordinates are illustrative geographic samples and schematic arrows are teaching geometry, not measured winds, elevations or boundary datasets.

## Western Ghats / Maharashtra

- UNESCO, Western Ghats: https://whc.unesco.org/en/list/1342/ — the mountain chain intercepts moisture-bearing southwest monsoon winds.
- Government of Maharashtra, About Pune: https://pune.gov.in/en/about-pune/ — rainfall varies from the western hill areas toward the eastern district; southwest monsoon is central to the pattern.
- NCERT Class 11 Geography, Climate chapter, hosted by IIT Kanpur SATHEE: https://sathee.iitk.ac.in/ncert-books/class-11/geography/india-physical-environment/chapter-04-climate/ — contrasts windward Ghats with leeward plateau in the monsoon season.

These support a general seasonal contrast; the lesson does not rank two weather stations or forecast a particular day's rain.

## Mechanism

- UK Met Office, Foehn effect: https://weather.metoffice.gov.uk/learn-about/weather/types-of-weather/wind/foehn-effect — orographic ascent/precipitation and mechanisms for warm, dry descending air. The lesson uses a simplified conceptual model; precipitation is affected by other processes too.

## Transfer: northern Andes

- NASA Earth Observatory, Looking Down on the Andes (2023): https://science.nasa.gov/earth/earth-observatory/looking-down-on-the-andes-151670/ — describes drier western Atacama and moisture delivered to eastern slopes from the continental interior.

The transfer scene covers northern Chile and the eastern Andean foothills around 22 degrees south. It must not be generalized to southern Patagonia, where prevailing westerlies often favour western slopes.

## Basemap and attribution

Google Earth supplies the actual imagery and terrain, subject to its availability and terms. Existing Earth attribution is preserved; our generated assets do not replace it. The package contains no satellite imagery downloads, official logos or external icon dependencies.


## Reviewed river lesson (accessed 2026-10-25)

- The Met, Art of the First Cities: https://www.metmuseum.org/exhibitions/listings/2003/art-of-the-first-cities : irrigation, damaging floods, cities and exchange.
- Spurlock Museum, Ancient Mesopotamia: https://www.spurlock.illinois.edu/exhibits/permanent/mso/ : water, irrigation, transport and soil.
- UCL Digital Egypt, Food Production: https://www.ucl.ac.uk/museums-static/digitalegypt/foodproduction/index.html : historical seasonal farming before modern dams.

The transfer drought question is an explicitly hypothetical causal application. Its diagram is not historical event data. Version 0.3.1 removes the guessed river lines: actual imagery shows the waterways; neutral comparison highlights and canal/field illustrations remain explicitly schematic.


## Camera and overlay implementation references

- Google KML touring: https://developers.google.com/kml/documentation/touring : native gx:Tour, Playlist and smooth FlyTo camera movements.
- Google KML reference: https://developers.google.com/kml/documentation/kmlreference : ScreenOverlay size=0 on one dimension preserves source image aspect ratio.
- The installed Harsh profile lg-kml-tours and lg-ssh-control instructions document playtour=NAME and exittour=true through /tmp/query.txt. Their runtime playback on this rig still requires live confirmation.
