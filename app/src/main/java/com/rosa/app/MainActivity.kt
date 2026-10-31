package com.rosa.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.*
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONObject

private val Ink = Color(0xFF090B14)
private val Panel = Color(0xFF151A2A)
private val Violet = Color(0xFF9875FF)
private val Cyan = Color(0xFF61DDF2)
private val White = Color(0xFFF2F3FA)
private data class ChatLine(val text: String, val mine: Boolean)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!Python.isStarted()) Python.start(AndroidPlatform(this))
        setContent { RosaHome() }
    }
}

@Composable
private fun RosaHome() {
    var input by remember { mutableStateOf("") }
    var language by remember { mutableStateOf("en") }
    val lines = remember { mutableStateListOf(ChatLine("Hi, I'm ROSA. Tell me what you need.", false)) }
    val pulse = rememberInfiniteTransition(label = "orb")
    val scale by pulse.animateFloat(0.96f, 1.04f, infiniteRepeatable(tween(1800), RepeatMode.Reverse), label = "scale")

    MaterialTheme(colorScheme = darkColorScheme(
        background = Ink, surface = Panel, primary = Violet, secondary = Cyan,
        onBackground = White, onSurface = White
    )) {
        Surface(Modifier.fillMaxSize(), color = Ink) {
            Column(Modifier.fillMaxSize().statusBarsPadding().navigationBarsPadding().padding(horizontal = 22.dp)) {
                Row(Modifier.fillMaxWidth().padding(top = 16.dp, bottom = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text("ROSA", color = White, fontSize = 25.sp, fontWeight = FontWeight.Bold, letterSpacing = 3.sp)
                        Text("YOUR PERSONAL AI", color = Cyan, fontSize = 10.sp, letterSpacing = 2.sp)
                    }
                    IconButton(onClick = { lines.add(ChatLine("Settings and secure AI connection will be available here.", false)) }) {
                        Icon(Icons.Default.Settings, null, tint = White)
                    }
                }
                Box(Modifier.fillMaxWidth().weight(0.40f), contentAlignment = Alignment.Center) {
                    Box(Modifier.size(210.dp).scale(scale).background(
                        Brush.radialGradient(listOf(Violet.copy(alpha=.28f), Cyan.copy(alpha=.09f), Color.Transparent)), CircleShape
                    ), contentAlignment = Alignment.Center) {
                        Box(Modifier.size(142.dp).background(
                            Brush.linearGradient(listOf(Color(0xFF493A8D), Color(0xFF142E50))), CircleShape
                        ).border(1.dp, Cyan.copy(alpha=.6f), CircleShape), contentAlignment = Alignment.Center) {
                            Box(Modifier.size(76.dp).background(
                                Brush.radialGradient(listOf(Color(0xFFB7A4FF), Violet, Color(0xFF253C70))), CircleShape
                            ))
                        }
                    }
                    Column(Modifier.align(Alignment.BottomCenter).padding(bottom = 12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("READY WHEN YOU ARE", color = Cyan, fontSize = 10.sp, letterSpacing = 2.sp)
                        Text("ROSA is listening", color = White.copy(alpha=.7f), fontSize = 13.sp)
                    }
                }
                Text("CONVERSATION", color = Violet, fontSize = 10.sp, letterSpacing = 2.sp, fontWeight = FontWeight.Bold)
                LazyColumn(Modifier.weight(0.60f).fillMaxWidth().padding(top = 10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    items(lines) { line ->
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = if (line.mine) Arrangement.End else Arrangement.Start) {
                            Surface(color = if (line.mine) Color(0xFF30264F) else Panel,
                                shape = RoundedCornerShape(18.dp), modifier = Modifier.widthIn(max = 300.dp)) {
                                Text(line.text, Modifier.padding(horizontal = 15.dp, vertical = 12.dp), color = White, fontSize = 14.sp)
                            }
                        }
                    }
                }
                Row(Modifier.fillMaxWidth().padding(vertical = 16.dp).background(Panel, RoundedCornerShape(28.dp)).padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically) {
                    BasicTextField(value = input, onValueChange = { input = it }, modifier = Modifier.weight(1f).padding(vertical = 10.dp),
                        textStyle = androidx.compose.ui.text.TextStyle(color = White, fontSize = 15.sp),
                        cursorBrush = androidx.compose.ui.graphics.SolidColor(Cyan),
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                        keyboardActions = KeyboardActions(onSend = { sendMessage(input, language, lines) { input = "" } }),
                        decorationBox = { inner -> if (input.isEmpty()) Text("Ask ROSA anything…", color = White.copy(alpha=.4f)); inner() })
                    IconButton(onClick = { sendMessage(input, language, lines) { input = "" } }, enabled = input.isNotBlank()) {
                        Icon(Icons.AutoMirrored.Filled.Send, "Send", tint = Cyan)
                    }
                }
                Row(Modifier.fillMaxWidth().padding(bottom = 10.dp), horizontalArrangement = Arrangement.Center) {
                    listOf("en" to "ENGLISH", "te" to "తెలుగు", "hi" to "हिन्दी").forEach { (code, label) ->
                        TextButton(onClick = { language = code }) {
                            Text(label, color = if (language == code) Cyan else White.copy(alpha=.45f), fontSize = 11.sp)
                        }
                    }
                }
            }
        }
    }
}

private fun sendMessage(text: String, language: String, lines: MutableList<ChatLine>, clear: () -> Unit) {
    val value = text.trim()
    if (value.isEmpty()) return
    lines.add(ChatLine(value, true))
    clear()
    try {
        val py = Python.getInstance()
        val result = py.getModule("rosa_bridge").callAttr("respond", value, language).toString()
        val obj = JSONObject(result)
        val response = obj.optString("text", "I couldn't process that.")
        lines.add(ChatLine(response, false))
        val action = obj.optJSONObject("action")
        if (action != null && action.optBoolean("requires_confirmation")) {
            lines.add(ChatLine("Device action proposed: ${action.optString("kind")}. Device confirmation flow is being connected.", false))
        }
    } catch (e: Exception) {
        lines.add(ChatLine("ROSA encountered an internal error. Please try again.", false))
    }
}
