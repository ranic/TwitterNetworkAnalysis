def get_feature(line):
    (_, _, result) = line.partition(":")
    return result.strip()

class Tweet:
    def __init__(self, lines, filename):
        for line in lines:
            if (line.startswith("Text:")):
                self.text = get_feature(line)
            elif (line.startswith("Time:")):
                self.time = get_feature(line).replace("CST","").replace("CDT","")
            elif (line.startswith("MentionedEntities:")):
                self.mentioned_entities = get_feature(line).split(" ")
            elif (line.startswith("Hashtags:")):
                self.hashtags = get_feature(line).split(" ")
            """if (line.startswith("Type:")):
                self.atype = get_feature(line)
            elif (line.startswith("Origin:")):
                self.origin = get_feature(line)
            elif (line.startswith("URL:")):
                self.url = get_feature(line)
            elif (line.startswith("ID:")):
                self.id = get_feature(line)"""
            """elif (line.startswith("RetCount:")):
                self.retcount = get_feature(line)
            elif (line.startswith("Favorite:")):
                self.favorite = get_feature(line)"""
        self.lines = lines

    def __str__(self):
        return "%s\nHashtag:%s" % ("\n".join(lines), self.hashtags)
