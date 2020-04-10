package com.n9mtq4.hdr2sdrlut

import java.awt.image.BufferedImage
import java.io.BufferedWriter
import java.io.File
import javax.imageio.ImageIO

/**
 * Created by will on 3/30/20 at 7:59 AM.
 *
 * @author Will "n9Mtq4" Bresnahan
 */

const val HDR_FRAMES_DIR = "/mnt/L4/media/clonewars/Season07/hdrluts/1080hdr"
const val SDR_FRAMES_DIR = "/mnt/L4/media/clonewars/Season07/hdrluts/1080"

const val CSV_SPLITS = 4

const val X_BLACK_BAR = 0
const val Y_BLACK_BAR = 132

const val SDR_START = 2
const val SDR_END = 30810 + 200

const val HDR_START = 74
const val HDR_END = 30882 + 200

const val FRAME_SELECTION = 1
const val X_SELECTION = 8 / (CSV_SPLITS / 2)
const val Y_SELECTION = 6 / (CSV_SPLITS / 2)

val X_RANDOM_RANGE = 0 until X_SELECTION
val Y_RANDOM_RANGE = 0 until Y_SELECTION

fun main() {
	
	val hdrFiles = File(HDR_FRAMES_DIR).listFiles()!!.sorted().subList(HDR_START - 1, HDR_END)
	val sdrFiles = File(SDR_FRAMES_DIR).listFiles()!!.sorted().subList(SDR_START - 1, SDR_END)
	
	assert(hdrFiles.size == sdrFiles.size)
	
	val fileMap = sdrFiles
		.zip(hdrFiles)
		.filterIndexed { i, _ -> i % FRAME_SELECTION == 0 }
	
	val data = fileMap
		.shuffled()
		.asSequence()
		.map { (sdrFile, hdrFile) -> ImageIO.read(sdrFile) to ImageIO.read(hdrFile) }
		.mapIndexed { index, (sdrImage, hdrImage) ->
			println("processing ${index + 1}/${fileMap.size}")
			csvProcessImage(sdrImage, hdrImage)
		}.flatten()
	
	val outputFiles = Array(CSV_SPLITS) { i -> File("s07e05_${i + 1}.csv") }
	val outputWriters = outputFiles.map { it.bufferedWriter() }
	
	outputWriters.forEach { writer -> 
		writer.write("hr,hg,hb,sr,sg,sb")
		writer.newLine()
	}
	
	data.chunked(CSV_SPLITS).forEach { chunk -> 
		
		assert(chunk.size == outputFiles.size)
		
		outputWriters.zip(chunk).forEach { (writer, entry) -> 
			val strLine = entry.joinToString(separator = ",")
			writer.write(strLine)
			writer.newLine()
		}
		
	}
	
	outputWriters.forEach(BufferedWriter::close)
	
}

fun csvProcessImage(sdrImage: BufferedImage, hdrImage: BufferedImage): List<List<String>> {
	
	assert(sdrImage.width == hdrImage.width)
	assert(sdrImage.height == hdrImage.height)
	
	val height = sdrImage.height - Y_BLACK_BAR
	val width = sdrImage.width - X_BLACK_BAR
	
	return (Y_BLACK_BAR until height step Y_SELECTION).map { y ->
		(X_BLACK_BAR until width step X_SELECTION).map { x ->
			val xOffset = X_RANDOM_RANGE.random()
			val yOffset = Y_RANDOM_RANGE.random()
			val cx = (x + xOffset).coerceIn(0, width)
			val cy = (y + yOffset).coerceIn(0, height)
			csvLinePixel(sdrImage, hdrImage, cx, cy)
		}
	}.flatten()
	
}

fun csvLinePixel(sdrImage: BufferedImage, hdrImage: BufferedImage, sdrx: Int, sdry: Int): List<String> {
	
	val sdrPixel = sdrImage.raster.getPixel(sdrx, sdry, IntArray(3))
	val hdrPixel = hdrImage.raster.getPixel(sdrx, sdry, IntArray(3))
	
	return (hdrPixel + sdrPixel).map { it.toString() }
	
}
