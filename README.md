Eve - The Event Processor
=========================

**This is still a draft and a project under heavy development!**

I was looking for a system that is able to read data (especially metrics) from different sources (like [RabbitMQ](https://www.rabbitmq.com/) or [CollectD](http://collectd.org)) transform it to something generic (preferrably json) and then push it to different backends (like [Riemann](http://riemann.io), [Graphite](http://graphite.wikidot.com) or [InfluxDB](http://influxdb.org)).

I had a look at [Logstash](http://logstash.net) but this was not flexible enough. It was impossible for me to configure it to use a CollectD input and a Graphite output in a way that the metrics in Graphite are in any way readable. I was also thinking about [Storm](http://storm.incubator.apache.org) and programming a topology by myself, but the overhead was far to much for me (and I hate [Zookeeper](http://zookeeper.apache.org)).

So I decided to build something new that would suite my needs (I really like to build something new...).
Eve is just a single process that loads plugins for ```input```, ```output``` and ```format``` reads from input, transforms it regarding the rules of format to json and kicks it out to the output plugin. Many instances of eve can run on the same server and it is easily scalable, depending on the input that you use. Just start more instances on other servers!

For now this is a "Works on my system" project, but I'm trying to build it as generic as possible. So maybe someone will find it interesting and/or usefull.

Usage
-----
 1. Clone me! ```git clone ```
 2. Configure logging here ```logging.json```
 3. Configure your inputs, output and formats here ```worker.json```
 4. Install requirements ```pip install -r requirements.txt```
 5. Give it a try and hope for the best! ```eve.py```

Writing your own Plugin
-----------------------

Coming soon!
