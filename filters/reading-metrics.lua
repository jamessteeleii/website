local function metadata_text(value)
  if value == nil then
    return ""
  end

  return pandoc.utils.stringify(value)
end

local function format_number(value)
  local digits = tostring(value)
  local formatted = digits:reverse():gsub("(%d%d%d)", "%1,"):reverse()
  return formatted:gsub("^,", "")
end

local function source_word_count()
  local input_file = quarto.doc.input_file
  if input_file == nil then
    return nil
  end

  local handle = io.open(input_file, "r")
  if handle == nil then
    return nil
  end

  local source = handle:read("*a")
  handle:close()

  source = source:gsub("\r\n", "\n")
  local body = source:match("^%-%-%-\n.-\n%-%-%-\n(.*)$") or source
  local _, spaces = body:gsub(" ", "")
  return spaces + 1
end

local function rendered_word_count(blocks)
  local plain = pandoc.write(pandoc.Pandoc(blocks), "plain")
  local _, spaces = plain:gsub(" ", "")
  return spaces + 1
end

function Pandoc(document)
  if metadata_text(document.meta.kind):lower() ~= "note" then
    return document
  end

  -- Quarto's listing pages estimate word count by splitting the source body on
  -- literal spaces. Repeating that method keeps the article and listing values
  -- identical while leaving the note source itself untouched.
  local words = source_word_count() or rendered_word_count(document.blocks)
  local minutes = math.max(1, math.ceil(words / 200))
  local word_label = words == 1 and "word" or "words"
  local minute_label = minutes == 1 and "minute" or "minutes"
  local visible_text = string.format("%s %s · %d min read", format_number(words), word_label, minutes)
  local accessible_text = string.format(
    "%s %s; estimated reading time: %d %s",
    format_number(words),
    word_label,
    minutes,
    minute_label
  )

  local metrics = pandoc.Div(
    { pandoc.Para({ pandoc.Str(visible_text) }) },
    pandoc.Attr("", { "reading-metrics" }, { ["aria-label"] = accessible_text })
  )

  table.insert(document.blocks, 1, metrics)
  return document
end
