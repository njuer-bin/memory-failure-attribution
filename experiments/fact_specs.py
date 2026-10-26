"""Authoritative atomic-fact decomposition for the round-3 gate annotation.

Each entry lists the propositions that the *reference answer* asserts in answer
to the row's question. Annotators only judge, per fact, whether the listed gold
evidence states it. Facts that are alternative phrasings of the same value share
a group id: the row passes if at least one member of the group is present.

Conventions used when authoring:

- Decompose the answer to the question, not incidental elaboration (a count is
  one fact; the list of items that produced the count is not re-checked unless
  the question asks for the items).
- Compound measures ("27 minutes and 45 seconds", "4 years and 9 months") stay
  one fact; comma/and lists of distinct entities become separate facts.
- LongMemEval ``_abs`` golds are negative facts: "the evidence mentions X" plus
  "the evidence does not mention Y".
- Dates are verbalised in full so a relative expression can be checked against
  the evidence's own timestamps.
"""
from __future__ import annotations

Fact = tuple[str, str | None]  # (text, any-of group id or None)

FACT_SPECS: dict[str, list[Fact]] = {
    # ---------------- LongMemEval ----------------
    "longmemeval-001": [("'Turbocharged Tuesdays' took place 4 days before 'Rack Fest'.", None)],
    "longmemeval-002": [("The narrator's highest score in Ticket to Ride is 132 points.", None)],
    "longmemeval-003": [("The narrator joined 'Page Turners' before 'Marketing Professionals'.", None)],
    "longmemeval-004": [
        ("The evidence mentions booking an Airbnb in San Francisco.", None),
        ("The evidence does not mention booking an Airbnb in Sacramento.", None),
    ],
    "longmemeval-005": [("The narrator gained the most followers on TikTok over the past month.", None)],
    "longmemeval-006": [("The narrator has met up with Alex from Germany twice.", None)],
    "longmemeval-007": [
        ("The evidence mentions trying Korean restaurants.", None),
        ("The evidence does not mention trying Italian restaurants.", None),
    ],
    "longmemeval-008": [("The narrator attended 3 graduation ceremonies in the past three months.", None)],
    "longmemeval-009": [("The narrator has completed 5 projects since starting painting classes.", None)],
    "longmemeval-010": [("The narrator earned $420 at the Downtown Farmers Market on the most recent visit.", None)],
    "longmemeval-011": [("The guitar was serviced at a music shop on Main St.", None)],
    "longmemeval-012": [("The narrator spent $270 more per night on accommodations in Hawaii than in Tokyo.", None)],
    "longmemeval-013": [("The narrator attended the 'Data Analysis using Python' webinar before the 'Effective Time Management' workshop.", None)],
    "longmemeval-014": [
        ("The evidence mentions a 10-day trip to Hawaii.", None),
        ("The evidence does not mention a trip to Seattle.", None),
    ],
    "longmemeval-015": [("The narrator flew United Airlines most often in March and April.", None)],
    "longmemeval-016": [("The narrator received the new phone case before losing the phone charger.", None)],
    "longmemeval-017": [("The new prime lens arrived before the road trip to the coast.", None)],
    "longmemeval-018": [
        ("The evidence mentions fixing the fence.", None),
        ("The evidence does not mention purchasing cows from Peter.", None),
    ],
    "longmemeval-019": [
        ("The evidence mentions starting the role of Senior Software Engineer.", None),
        ("The evidence does not mention the role of Software Engineer Manager.", None),
    ],
    "longmemeval-020": [
        ("The narrator attended the Holiday Market 7 days before buying the iPhone 13 Pro.", "g1"),
        ("The narrator attended the Holiday Market 8 days before buying the iPhone 13 Pro, counting the last day.", "g1"),
    ],
    "longmemeval-021": [("The narrator took social media breaks totaling 17 days.", None)],
    "longmemeval-022": [("The evidence does not mention a 30-gallon fish tank.", None)],
    "longmemeval-023": [("There are 25 titles on the narrator's to-watch list.", None)],
    "longmemeval-024": [("The narrator watched 5 MCU films in the last 3 months.", None)],
    "longmemeval-025": [("The narrator took the solo trip to Thailand before the family trip to Europe.", None)],
    "longmemeval-026": [("The evidence indicates the narrator visited 0 museums or galleries in December.", None)],
    "longmemeval-027": [("The narrator currently has 2 magazine subscriptions.", None)],
    "longmemeval-028": [("The narrator has added 25 new postcards since starting to collect again.", None)],
    "longmemeval-029": [("The narrator had been accepted into the exchange program one week before starting the pre-departure orientation sessions.", None)],
    "longmemeval-030": [("The narrator spent $2,500 on luxury items in the past few months.", None)],
    "longmemeval-031": [("The narrator purchased or downloaded 3 music albums or EPs.", None)],
    "longmemeval-032": [("The narrator's most recent family trip was to Paris.", None)],
    "longmemeval-033": [
        ("Previously, the narrator played tennis with friends at the local park every week on Sunday.", None),
        ("Currently, the narrator plays tennis every other week on Sunday.", None),
    ],
    "longmemeval-034": [("The narrator spent $720 on workshops in the last four months.", None)],
    "longmemeval-035": [
        ("The evidence mentions collecting autographed baseballs.", None),
        ("The evidence does not mention collecting autographed footballs.", None),
    ],
    "longmemeval-036": [("The narrator is currently obsessed with Kansas City Masterpiece BBQ sauce.", None)],
    "longmemeval-037": [("The narrator took care of the bike before the car in February.", None)],
    "longmemeval-038": [
        ("The evidence mentions 4 years in high school (2010-2014).", None),
        ("The evidence mentions 2 years at PCC (2014-2016).", None),
        ("The evidence mentions 4 years at UCLA (2016-2020).", None),
        ("The evidence does not state the duration or completion date of the Master's degree.", None),
    ],
    "longmemeval-039": [("The narrator takes a cocktail-making class on Friday.", None)],
    "longmemeval-040": [("The narrator's previous personal best charity 5K time was 27 minutes and 45 seconds.", None)],
    "longmemeval-041": [("The narrator has tried 4 Korean restaurants in the city.", None)],
    "longmemeval-042": [("The narrator cleaned white Adidas sneakers last month.", None)],
    "longmemeval-043": [("The narrator has lived in the current Harajuku apartment for 3 months.", None)],
    "longmemeval-044": [
        ("The narrator attended three weddings this year.", None),
        ("One couple was Rachel and Mike.", None),
        ("One couple was Emily and Sarah.", None),
        ("One couple was Jen and Tom.", None),
    ],
    "longmemeval-045": [("The narrator has completed 23 pieces of writing since starting to write again three weeks ago.", None)],
    "longmemeval-046": [
        ("21 days passed between Holi and the Sunday mass at St. Mary's Church.", "g1"),
        ("22 days (including the last day) passed between Holi and the Sunday mass at St. Mary's Church.", "g1"),
    ],
    "longmemeval-047": [("The narrator serviced or planned to service 2 bikes in March.", None)],
    "longmemeval-048": [("The narrator spent the most money at Thrive Market in the past month.", None)],
    "longmemeval-049": [("The narrator needs 120 stars to reach the gold level on the Starbucks Rewards app.", None)],
    "longmemeval-050": [("The narrator attended 5 sessions of the bereavement support group.", None)],
    "longmemeval-051": [("The narrator spent 3 days attending workshops, lectures, and conferences in April.", None)],
    "longmemeval-052": [("Alex became a parent before Rachel.", None)],
    "longmemeval-053": [
        ("The evidence mentions getting the iPhone 13 Pro.", None),
        ("The evidence mentions attending the market.", None),
        ("The evidence does not mention buying an iPad.", None),
    ],
    "longmemeval-054": [("The narrator has completed 30 videos of Corey Schafer's Python programming series.", None)],
    "longmemeval-055": [("The evidence indicates the narrator has a spare screwdriver for opening the laptop.", None)],
    "longmemeval-056": [
        ("The evidence mentions living in Harajuku.", None),
        ("The evidence does not mention living in Shinjuku.", None),
    ],
    "longmemeval-057": [("The narrator currently has 3 tanks, including the one set up for the friend's kid.", None)],
    "longmemeval-058": [("The narrator finished 'The Hate U Give' before 'The Nightingale'.", None)],
    "longmemeval-059": [("The narrator attends yoga classes three times a week.", None)],
    "longmemeval-060": [("The narrator has spent $185 on bike-related expenses since the start of the year.", None)],
    "longmemeval-061": [("The narrator's mom uses the same grocery list method as the narrator.", None)],
    "longmemeval-062": [("The narrator has led or is currently leading 2 projects.", None)],
    "longmemeval-063": [("The narrator watched 15 Crash Course videos in the past few weeks.", None)],
    "longmemeval-064": [("The narrator most recently increased the coffee limit from one cup to two cups.", None)],
    "longmemeval-065": [("The narrator viewed four properties before making an offer on the Brookside townhouse.", None)],
    "longmemeval-066": [
        ("The evidence mentions Alex becoming a parent in January.", None),
        ("The evidence does not mention Tom becoming a parent.", None),
    ],
    "longmemeval-067": [("The narrator currently has 1300 Instagram followers.", None)],
    "longmemeval-068": [
        ("30 days passed between the Sunday mass at St. Mary's Church and the Ash Wednesday service at the cathedral.", "g1"),
        ("31 days (including the last day) passed between the Sunday mass and the Ash Wednesday service.", "g1"),
    ],
    "longmemeval-069": [
        ("The evidence mentions playing tennis.", None),
        ("The evidence does not mention playing table tennis.", None),
    ],
    "longmemeval-070": [("The narrator met the woman selling jam at the farmer's market before the tourist from Australia.", None)],
    "longmemeval-071": [("The narrator was pre-approved for $400,000 on the Wells Fargo mortgage.", None)],
    "longmemeval-072": [("The evidence indicates the narrator has not started working at Google yet.", None)],
    "longmemeval-073": [("It took the narrator 3.5 weeks to watch all MCU movies and the main Star Wars films.", None)],
    "longmemeval-074": [("The narrator took the family road trip across the American Southwest before the solo trip to Europe.", None)],
    "longmemeval-075": [("The narrator usually goes to the gym at 6:00 pm.", None)],
    "longmemeval-076": [("The narrator is currently working on a Ford F-150 pickup truck.", None)],
    "longmemeval-077": [("The narrator currently owns 4 bikes.", None)],
    "longmemeval-078": [("The first BBQ event the narrator attended in June was on June 3rd.", None)],
    "longmemeval-079": [("The narrator has been working on 2 projects simultaneously, excluding the thesis.", None)],
    "longmemeval-080": [("The narrator got an Instant Pot before the Air Fryer.", None)],
    "longmemeval-081": [("The narrator had been a member of 'Book Lovers Unite' for two weeks when attending the meetup.", None)],
    "longmemeval-082": [("The narrator's personal best charity 5K time was 25 minutes and 50 seconds.", None)],
    "longmemeval-083": [("The narrator worked for 4 years and 9 months before starting the current job at NovaTech.", None)],
    "longmemeval-084": [
        ("When starting as Senior Software Engineer, the narrator led 4 engineers.", None),
        ("The narrator now leads 5 engineers.", None),
    ],
    "longmemeval-085": [("The narrator replaced or fixed five kitchen items.", None)],
    "longmemeval-086": [("The narrator wakes up at 7:30 am on Saturday mornings.", None)],
    "longmemeval-087": [("The narrator has learned to cook or tried 4 different cuisines in the past few months.", None)],
    "longmemeval-088": [("The evidence does not mention baking egg tarts.", None)],
    "longmemeval-089": [("The narrator acquired 3 plants in the last month.", None)],
    "longmemeval-090": [("The narrator needs to pick up or return 3 items of clothing from a store.", None)],
    "longmemeval-091": [("The narrator has worn the new black Converse Chuck Taylor All Star sneakers six times.", None)],
    "longmemeval-092": [("The narrator added 15 autographed baseballs in the first three months of collecting.", None)],
    "longmemeval-093": [("Before buying the gravel bike, the narrator had a road bike in addition to the mountain bike and the commuter bike.", None)],
    "longmemeval-094": [
        ("14 days passed between the 'Walk for Hunger' event and the 'Coastal Cleanup' event.", "g1"),
        ("8 days (including the last day) passed between the 'Walk for Hunger' and 'Coastal Cleanup' events.", "g1"),
    ],
    "longmemeval-095": [("The total hours of jogging and yoga the narrator did last week was 0.5 hours.", None)],
    "longmemeval-096": [
        ("The evidence mentions seeing Dr. Smith.", None),
        ("The evidence does not mention seeing Dr. Johnson.", None),
    ],
    "longmemeval-097": [("The narrator plans to stay in Oahu for the birthday trip to Hawaii.", None)],
    "longmemeval-098": [("The narrator rode rollercoasters 10 times across events from July to October.", None)],
    "longmemeval-099": [("The narrator met Tom before Mark and Sarah.", None)],
    "longmemeval-100": [("The narrator currently has 600 Instagram followers.", None)],
    # ---------------- LoCoMo ----------------
    "locomo-001": [
        ("Jon and Gina both lost their jobs.", None),
        ("Jon and Gina both decided to start their own businesses.", None),
    ],
    "locomo-002": [("Melanie read 'Becoming Nicole' based on Caroline's suggestion.", None)],
    "locomo-003": [
        ("Caroline is likely to pursue counseling.", "g1"),
        ("Caroline is likely to pursue mental health.", "g1"),
    ],
    "locomo-004": [
        ("Melanie went to the pottery workshop on the Friday before 15 July 2023.", "g1"),
        ("Melanie went to the pottery workshop on July 14, 2023.", "g1"),
    ],
    "locomo-005": [
        ("Caroline joined an activist group.", None),
        ("Caroline went to pride parades.", None),
        ("Caroline participated in an art show.", None),
        ("Caroline participated in a mentoring program.", None),
    ],
    "locomo-006": [("It took Jon five months to open his studio.", None)],
    "locomo-007": [("The evidence indicates Caroline does not intend to move back to her home country soon.", None)],
    "locomo-008": [("Melanie made the black and white bowl in the photo.", None)],
    "locomo-009": [
        ("Gina designed the limited hoodie collection in June 2023.", "g1"),
        ("Gina designed the limited hoodie collection in the week before 21 June 2023.", "g1"),
    ],
    "locomo-010": [("Both Jon and Gina participated in dance competitions.", None)],
    "locomo-011": [("The song 'Brave' by Sara Bareilles motivates Caroline.", None)],
    "locomo-012": [
        ("Jon lost his job.", None),
        ("Jon decided to start his own business to share his passion.", None),
    ],
    "locomo-013": [
        ("Melanie ran the charity race on the Saturday before 25 May 2023.", "g1"),
        ("Melanie ran the charity race on May 20, 2023.", "g1"),
    ],
    "locomo-014": [("Gina says the dancers in the photo look graceful.", None)],
    "locomo-015": [("On 1 February 2023, Gina found the perfect spot for her clothing store.", None)],
    "locomo-016": [
        ("Caroline applied to adoption agencies in the week of 23 August 2023.", "g1"),
        ("Caroline applied to adoption agencies from August 21, 2023 to August 27, 2023.", "g1"),
    ],
    "locomo-017": [
        ("Melanie bought figurines.", None),
        ("Melanie bought shoes.", None),
    ],
    "locomo-018": [("Melanie would be more interested in going to a national park than a theme park.", None)],
    "locomo-019": [("Jon is currently reading 'The Lean Startup'.", None)],
    "locomo-020": [("Gina said creating an experience for customers makes them want to come back.", None)],
    "locomo-021": [("Melanie saw a sign at the cafe stating that someone is not able to leave.", None)],
    "locomo-022": [("Melanie got into running to de-stress and clear her mind.", None)],
    "locomo-023": [
        ("Jon participated in a fair to promote his business.", None),
        ("Jon participated in networking events to promote his business.", None),
    ],
    "locomo-024": [
        ("Gina reminds herself of her successes and progress.", None),
        ("Gina has a support system.", None),
        ("Gina focuses on why she started.", None),
    ],
    "locomo-025": [("Gina was accepted for a fashion internship on May 23, 2023.", None)],
    "locomo-026": [
        ("Jon's dance studio offers one-on-one mentoring and training to dancers.", None),
        ("Jon's dance studio offers workshops and classes to local schools and centers.", None),
    ],
    "locomo-027": [
        ("Caroline is supported by her mentors.", None),
        ("Caroline is supported by her family.", None),
        ("Caroline is supported by her friends.", None),
    ],
    "locomo-028": [
        ("Caroline learned a lesson about self-acceptance.", None),
        ("Caroline learned a lesson about finding support.", None),
    ],
    "locomo-029": [("Melanie went to the park on 27 August 2023.", None)],
    "locomo-030": [("After the accident, Melanie feels her family is important and means the world to her.", None)],
    "locomo-031": [("Gina interviewed for a design internship on 10 May 2023.", None)],
    "locomo-032": [
        ("Caroline likes reading.", None),
        ("Caroline wants to be a counselor.", None),
    ],
    "locomo-033": [
        ("Caroline joined the new activist group on the Tuesday before 20 July 2023.", "g1"),
        ("Caroline joined the new activist group on July 18, 2023.", "g1"),
    ],
    "locomo-034": [("Caroline recommended 'Becoming Nicole' to Melanie.", None)],
    "locomo-035": [
        ("Melanie got hurt (had an accident).", None),
        ("Melanie had to take a break from pottery.", None),
    ],
    "locomo-036": [
        ("Melanie plays the clarinet.", None),
        ("Melanie plays the violin.", None),
    ],
    "locomo-037": [("Caroline and Melanie went to a pride festival together in 2022.", None)],
    "locomo-038": [
        ("Melanie has cats.", None),
        ("Melanie has a dog.", None),
    ],
    "locomo-039": [
        ("Gina's tattoo symbolizes freedom.", None),
        ("Gina's tattoo symbolizes expressing herself through dance.", None),
    ],
    "locomo-040": [
        ("Melanie thinks Caroline is doing something amazing.", None),
        ("Melanie thinks Caroline will be an awesome mom.", None),
    ],
    "locomo-041": [("Melanie and Caroline describe their journey together as an ongoing adventure of learning and growing.", None)],
    "locomo-042": [("The adoption agency supports LGBTQ+ individuals.", None)],
    "locomo-043": [("Mel and her kids made pots during the pottery workshop.", None)],
    "locomo-044": [("Caroline shared an abstract painting with blue streaks on a wall on October 13, 2023.", None)],
    "locomo-045": [("Gina's team performed 'Finding Freedom' and won first place.", None)],
    "locomo-046": [("Jon went to a fair on 24 April 2023.", None)],
    "locomo-047": [("Gina got her tattoo a few years ago.", None)],
    "locomo-048": [("Gina's favorite style of dance is contemporary.", None)],
    "locomo-049": [("Oliver once hid his bone in Melanie's slipper.", None)],
    "locomo-050": [("Gina's favorite dancing memory is winning first place at a regionals dance competition.", None)],
    "locomo-051": [
        ("Melanie read 'Nothing is Impossible'.", None),
        ("Melanie read 'Charlotte's Web'.", None),
    ],
    "locomo-052": [("Melanie signed up for a pottery class on 2 July 2023.", None)],
    "locomo-053": [("Caroline moved from Sweden four years ago.", None)],
    "locomo-054": [
        ("Jon started learning marketing and analytics tools on 9 July 2023.", "g1"),
        ("Jon started learning marketing and analytics tools in July 2023.", "g1"),
    ],
    "locomo-055": [("Mel and her kids painted a sunset with a palm tree in July 2023.", None)],
    "locomo-056": [
        ("The hand-painted bowl reminds Melanie of art.", None),
        ("The hand-painted bowl reminds Melanie of self-expression.", None),
    ],
    "locomo-057": [("Caroline wants to create a safe and inviting place for people to grow.", None)],
    "locomo-058": [("Jon said creating a special experience is the key to making customers feel welcome and come back.", None)],
    "locomo-059": [
        ("Caroline chose the adoption agency because of its inclusivity.", None),
        ("Caroline chose the adoption agency because of its support for LGBTQ+ individuals.", None),
    ],
    "locomo-060": [
        ("Caroline had the negative experience on a hike in the week before 25 August 2023.", "g1"),
        ("Caroline had the negative experience on a hike from August 14, 2023 to August 20, 2023.", "g1"),
    ],
    "locomo-061": [("Melanie has been creating art for seven years.", None)],
    "locomo-062": [
        ("Caroline decided to pursue counseling for transgender people.", "g1"),
        ("Caroline decided to pursue mental health for transgender people.", "g1"),
    ],
    "locomo-063": [("Gina's store is doing great.", None)],
    "locomo-064": [
        ("Melanie's family went on the roadtrip the weekend before 20 October 2023.", "g1"),
        ("Melanie's family went on the roadtrip from October 14, 2023 to October 15, 2023.", "g1"),
    ],
    "locomo-065": [
        ("Caroline advises doing research.", None),
        ("Caroline advises finding an adoption agency or lawyer.", None),
        ("Caroline advises gathering necessary documents.", None),
        ("Caroline advises preparing emotionally.", None),
    ],
    "locomo-066": [("Melanie realized that self-care is important.", None)],
    "locomo-067": [("Melanie goes to the beach with her kids once or twice a year.", None)],
    "locomo-068": [
        ("Caroline had a picnic in the week before 6 July 2023.", "g1"),
        ("Caroline had a picnic from June 26, 2023 to July 2, 2023.", "g1"),
    ],
    "locomo-069": [
        ("Melanie has been practicing art since 2016.", "g1"),
        ("Melanie has been practicing art for seven years.", "g1"),
    ],
    "locomo-070": [
        ("Melanie roasts marshmallows with her family on hikes.", None),
        ("Melanie tells stories with her family on hikes.", None),
    ],
    "locomo-071": [
        ("Gina wanted customers to feel cozy in her store.", "g1"),
        ("Gina wanted customers to feel comfortable in her store.", "g1"),
        ("Gina wanted customers to feel that the store is inviting.", "g1"),
    ],
    "locomo-072": [("Caroline has a guinea pig.", None)],
    "locomo-073": [
        ("Gina was accepted for the design internship on 27 May 2023.", "g1"),
        ("Gina was accepted for the design internship in May 2023.", "g1"),
    ],
    "locomo-074": [("Caroline is single.", None)],
    "locomo-075": [("Jon hosted a dance competition in May 2023.", None)],
    "locomo-076": [("Jon's favorite style of dance is contemporary.", None)],
    "locomo-077": [("Caroline's grandma is from Sweden.", None)],
    "locomo-078": [("Jon lost his job as a banker on 19 January 2023.", None)],
    "locomo-079": [("Melanie showed Caroline a painting inspired by sunsets with a pink sky on October 13, 2023.", None)],
    "locomo-080": [("Gina lost her job at Door Dash in January 2023.", None)],
    "locomo-081": [
        ("Gina went to a dance class with friends in July 2023.", "g1"),
        ("Gina went to a dance class with friends on the Friday before 23 July 2023.", "g1"),
        ("Gina went to a dance class with friends in the middle of July.", "g1"),
    ],
    "locomo-082": [("Melanie is a fan of Ed Sheeran.", None)],
    "locomo-083": [("Melanie supports the transgender community.", None)],
    "locomo-084": [("Caroline is a transgender woman.", None)],
    "locomo-085": [
        ("Flowers represent growth to Melanie.", None),
        ("Flowers represent beauty to Melanie.", None),
        ("Flowers remind Melanie to appreciate the small moments.", None),
        ("Flowers were part of Melanie's wedding decor.", None),
    ],
    "locomo-086": [("Mel and her kids made a cup with a dog face on it.", None)],
    "locomo-087": [("Melanie went on a hike on 19 October 2023.", None)],
    "locomo-088": [("Caroline saw many people at the council meeting who want to create loving homes for children in need.", None)],
    "locomo-089": [("Melanie and her family saw the Perseid meteor shower during their camping trip last year.", None)],
    "locomo-090": [("Melanie's friend adopted a child in 2022.", None)],
    "locomo-091": [("Caroline attended an LGBTQ+ counseling workshop recently.", None)],
    "locomo-092": [
        ("Caroline passed the adoption interview on the Friday before 22 October 2023.", "g1"),
        ("Caroline passed the adoption interview on October 20, 2023.", "g1"),
    ],
    "locomo-093": [("Jon's group is performing at a festival in February 2023.", None)],
    "locomo-094": [("Gina describes Jon's studio as amazing.", None)],
    "locomo-095": [
        ("Caroline was inspired by visiting an LGBTQ center.", None),
        ("Caroline wanted to capture unity and strength.", None),
    ],
    "locomo-096": [
        ("It was a transgender poetry reading.", None),
        ("Transgender people shared their stories there.", None),
    ],
    "locomo-097": [
        ("The workshop discussed therapeutic methods.", None),
        ("The workshop discussed how to best work with trans people.", None),
    ],
    "locomo-098": [("The posters at the poetry reading read 'Trans Lives Matter'.", None)],
    "locomo-099": [("Jon and Gina started businesses based on what they love.", None)],
    "locomo-100": [
        ("Caroline attended a transgender poetry reading.", None),
        ("Caroline attended a conference.", "g1"),
        ("Caroline attended a counseling workshop.", "g1"),
    ],
}
