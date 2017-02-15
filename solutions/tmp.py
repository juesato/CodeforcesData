import re
OUTPUT_BEGIN_RE = re.compile('<div class="name">Participant\'s output</div>\s+<div class="text"><pre>(.*?)</pre>', re.DOTALL)
# OUTPUT_BEGIN = '<div class="name">Participant\'s output</div>\s+<div class="text"><pre>'

s = """
<div class="name">Participant's output</div>
    <div class="text"><pre>CHAT WITH HER!
</pre></div>
</div>
<div c
"""

s = """
                        $(this).find("tr:last td").addClass("bottom");
                        $(this).find("tr:odd td").addClass("dark");
                        $(this).find("tr td:first-child, tr th:first-child").addClass("left");
                        $(this).find("tr td:last-child, tr th:last-child").addClass("right");
                    });

                    $(".datatable table.tablesorter").each(function () {
                        $(this).bind("sortEnd", function () {
                            $(".datatable").each(function () {
                                $(this).find("th, td")
                                    .removeClass("top").removeClass("bottom")
                                    .removeClass("left").removeClass("right")
                                    .removeClass("dark");
                                $(this).find("tr:first th").addClass("top");
                                $(this).find("tr:last td").addClass("bottom");
                                $(this).find("tr:odd td").addClass("dark");
                                $(this).find("tr td:first-child, tr th:first-child").addClass("left");
                                $(this).find("tr td:last-child, tr th:last-child").addClass("right");
                            });
                        });
                    });
                }
        });
    </script>

    <div class="roundbox " style="margin-top:2em;font-size:1.1rem;">
            <div class="roundbox-lt">&nbsp;</div>
            <div class="roundbox-rt">&nbsp;</div>
        <div class="caption titled">&rarr; Source
            <div class="top-links">
            </div>
        </div>
    <pre class="prettyprint lang-java program-source" style="padding: 0.5em;">import java.util.*;

public class PoliceRecruits {

    public static void main(String[] args) {
        Scanner kb = new Scanner(System.in);
        int n = kb.nextInt();

        long buf = 0;
        int numUntreated = 0;
        for (int i = 0; i < n; i++) {
            long k = kb.nextLong();
            if (k > 0)
                buf += k;
            else {
                if (buf - 1 < 0)
                    numUntreated++;
                else
                    buf--;
            }
        }
        System.out.println(numUntreated);
    }

"""

SOURCE_CODE_BEGIN = 'program-source" style="padding: 0.5em;">'

print (s.find(SOURCE_CODE_BEGIN, 0))

for a in OUTPUT_BEGIN_RE.finditer(s):
    print 'good'
    print a.group(1)