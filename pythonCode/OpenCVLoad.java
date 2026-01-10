package com.crawljax.stateabstractions.visual;

public class OpenCVLoad {
	private static boolean loaded = false;

	public static boolean load() {
		if (loaded) {
			return true;
		}
		String dllPath = System.getenv("OPENCV_DLL");
		if (dllPath == null || dllPath.trim().isEmpty()) {
			dllPath = System.getProperty("opencv.dll");
		}
		if (dllPath != null && !dllPath.trim().isEmpty()) {
			System.load(dllPath);
		} else {
			System.loadLibrary("opencv_java");
		}
		loaded = true;
		return true;
	}
}
