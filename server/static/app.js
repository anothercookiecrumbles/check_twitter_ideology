(function() {

    // If we get a _proper_ response from the server, let's run through the
    // motions: show error if error, else display the bubbles.
    function success(response) {

        var parsed_response = JSON.parse(response)
        if (parsed_response["Error"] != undefined) {
            // Should probably factor this into a separate error function so we
            // don't have p styles everywhere but meh.
            $("#messages").empty().append("<p style='color:#cc0000;'>" + response['Error'] + ".</p>")
            return
        }

        // OK, so if we're here, it means we don't need messages.
        $("#messages p").remove();

        // re-enable button
        $("#button").removeClass("disabled");

        // add header above visualization
        $("#messages").append("<h2>@" + parsed_response["handle"] + "'s Twitter bubble.</h2>")

        showBubbles(parsed_response);
    }

    function clear() {
        $("svg").remove()
        $("#messages h2").remove();
        $(".tooltip p").remove();
    }

    // THIS CODE IS COPIED (AND MODIFIED) FROM
    // https://coderwall.com/p/z8uxzw/javascript-color-blender
    /*
     * convert a Number to a two character hex string
     * must round, or we will end up with more digits than
     * expected (2)
     * note: can also result in single digit, which will
     * need to be padded with a 0 to the left
     * @param: num         => the number to conver to
     * hex
     * @returns: string    => the hex representation
     * of the provided number
     * */
    function int_to_hex(num) {
        var hex = Math.round(num).toString(16);
        if (hex.length == 1)
            hex = '0' + hex;
        return hex;
    }

    function normalise_nodes(scores) {
        var classes = [];

        function create(node) {
            for (var item in node) {
                x = node[item]
                classes.push({
                    className: x[0],
                    value: x[2],
                    score: x[1]
                });
            }
        }
        create(scores);
        return {
            children: classes
        };
    }

    // Create the actual display/chart/bubbles.
    function showBubbles(response) {

        scores = response["friends"]

        margin = 10;

        var diameter = $("#bubbles").width() - margin,
            format = d3.format(",d");

        var bubble = d3.layout.pack()
            .sort(function(a, b) {
                return -(a.score - b.score);
            })
            .size([diameter, diameter])
            .padding(2);

        var svg = d3.select("#bubbles").append("svg")
            .attr("width", diameter)
            .attr("height", diameter)
            .attr("class", "bubble");

        var node = svg.selectAll(".node")
            .data(bubble.nodes(normalise_nodes(scores))
                .filter(function(d) {
                    return !d.children;
                }))
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            });

        node.append("circle")
            .attr("r", function(d) {
                return d.r;
            })
            .attr("fill", function(d) {
                // OK, let's get creative here.
                // We need to use colours in proportion to, well, the score.
                // So, what we do is we check if the score is less than 50,
                // and if so, we up the blue, but still keep some red.
                // code from:
                // https://coderwall.com/p/z8uxzw/javascript-color-blender
                //
                base_red = '#CC0000'
                base_blue = '#0000CF'

                if (d.score < 0) {
                    return "rgba(50,205,5085,1)";
                }
                if (d.score > 1) {
                    d.score = 1;
                }

                if (d.score <= 0.5) {
                    rgba = blend_colors(base_red, base_blue, 1 - d.score).toString()
                }

                if (d.score > 0.5) {
                    rgba = blend_colors(base_red, base_blue, d.score).toString()
                }

                return "rgba(" + rgba + ")";
            });

        node.append("text")
            .text(function(d) {
                return d.className.substring(0, d.r / 3)
            })
            .attr("text-anchor", "middle")
            .style("font-size", function(d) {
                return Math.min(2 * d.r, (2 * d.r - 8) / this.getComputedTextLength() * 10) + "px";
            })
            .attr("dy", ".3em");


        node.on("mouseover", function(d) {
            $(".tooltip").empty().append("<p> " + d.className + "</p>")
        });
    }

    /*
    THIS HAS BEEN COPIED (BUT MODIFIED)
    blend two colors to create the color that is at the percentage away from the first color
    this is a 5 step process
        1: validate input
        2: convert input to 6 char hex
        3: convert hex to rgb
        4: take the percentage to create a ratio between the two colors
        5: convert blend to hex
    @param: color1      => the first color, hex (ie: #000000)
    @param: color2      => the second color, hex (ie: #ffffff)
    @param: percentage  => the distance from the first color, as a decimal between 0 and 1 (ie: 0.5)
    @returns: string    => the third color, hex, represenatation of the blend between color1 and color2 at the given percentage
    */
    function blend_colors(color1, color2, percentage) {
        // check input
        color1 = color1 || '#000000';
        color2 = color2 || '#ffffff';
        percentage = percentage || 0.5;

        // 1: validate input, make sure we have provided a valid hex
        if (color1.length != 4 && color1.length != 7)
            throw new error('colors must be provided as hexes');

        if (color2.length != 4 && color2.length != 7)
            throw new error('colors must be provided as hexes');

        if (percentage > 1 || percentage < 0)
            throw new error('percentage must be between 0 and 1');

        // 2: check to see if we need to convert 3 char hex to 6 char hex, else slice off hash
        //      the three character hex is just a representation of the 6 hex where each character is repeated
        //      ie: #060 => #006600 (green)
        if (color1.length == 4)
            color1 = color1[1] + color1[1] + color1[2] + color1[2] + color1[3] + color1[3];
        else
            color1 = color1.substring(1);
        if (color2.length == 4)
            color2 = color2[1] + color2[1] + color2[2] + color2[2] + color2[3] + color2[3];
        else
            color2 = color2.substring(1);

        // 3: we have valid input, convert colors to rgb
        color1 = [parseInt(color1[0] + color1[1], 16), parseInt(color1[2] + color1[3], 16), parseInt(color1[4] + color1[5], 16)];
        color2 = [parseInt(color2[0] + color2[1], 16), parseInt(color2[2] + color2[3], 16), parseInt(color2[4] + color2[5], 16)];

        console.log('hex -> rgba: c1 => [' + color1.join(', ') + '], c2 => [' + color2.join(', ') + ']');

        // 4: blend
        var color3 = [
            Math.trunc((1 - percentage) * color1[0] + percentage * color2[0]),
            Math.trunc((1 - percentage) * color1[1] + percentage * color2[1]),
            Math.trunc((1 - percentage) * color1[2] + percentage * color2[2]), 1.0
        ];

        // return rgba
        return color3;
    }

    // submit request.
    $("form").on("submit", function(e) {
        e.preventDefault();

        var twitter_handle = $("input[name=twitter_handle]").val().trim();

        // strip out the @ if it's been manually entered.
        if (twitter_handle.charAt(0) == '@') {
            twitter_handle = twitter_handle.substr(1)
        }

        // only call the server if the input is valid. I wonder if we can make
        // do some more sensible validations here?
        if (twitter_handle.trim().length > 0) {
            // update status
            $("#messages").append("<p style='color:#000099;'>Looking up who @" + twitter_handle + " is following...</p>");
            // clear existing data (if any)
            clear();
            // make request
            $.ajax({
                url: "/search/" + twitter_handle,
                type: "POST",
                success: function(data) {
                    success(data);
                },
                error: function(data) {
                    console.log(data)
                    $("#messages").empty().append("<p style='color:#cc0000;'>Error: " + data + "</p>")
                }
            });
        } else {
            //Inform user, because you know, even though JavaScript is terrible,
            //we're not.
            $("#messages").empty().append("<p style='color:#cc0000;'>No Twitter handle entered.</p>")
                //Re-enable the button.
            $("#button").removeClass("disabled");
        }

        // disable submit button
        $("button").addClass("disabled");
    });

})();
