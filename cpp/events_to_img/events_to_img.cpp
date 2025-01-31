#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <iomanip> // std::setw, std::setfillに必要
#include <algorithm>
#include <opencv2/opencv.hpp>
#include "H5Cpp.h"
#include <filesystem> // 必要に応じて追加（C++17以上）

using namespace H5;

// イベントデータ構造体
struct Event {
    uint16_t x; // x座標
    uint16_t y; // y座標
    int16_t p;  // 極性
    int64_t t;  // タイムスタンプ
};

// パス結合を行う関数
std::string join_path(const std::string& base, const std::string& sub) {
    if (base.empty()) return sub;
    if (sub.empty()) return base;
    if (base.back() == '/' || base.back() == '\\') { // ← 修正: '\\' にエスケープ
        return base + sub;
    } else {
        return base + "/" + sub;
    }
}

// トリガーファイルを読み込む関数
std::vector<int64_t> load_triggers(const std::string& trigger_file) {
    std::vector<int64_t> triggers;
    std::ifstream file(trigger_file);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open trigger file: " + trigger_file);
    }
    std::string line;
    while (std::getline(file, line)) {
        triggers.push_back(std::stoll(line));
    }
    return triggers;
}

// HDF5ファイルからイベントデータを読み込む
std::vector<Event> load_events_from_hdf5(const std::string& hdf5_file) {
    H5File file(hdf5_file, H5F_ACC_RDONLY);
    
    // データセットを開く
    DataSet p_dataset = file.openDataSet("/events/p");
    DataSet t_dataset = file.openDataSet("/events/t");
    DataSet x_dataset = file.openDataSet("/events/x");
    DataSet y_dataset = file.openDataSet("/events/y");

    // データサイズを取得
    DataSpace dataspace = p_dataset.getSpace();
    hsize_t dims[1];
    dataspace.getSimpleExtentDims(dims, nullptr);
    size_t num_events = dims[0];

    // メモリ確保
    std::vector<uint8_t> p_data(num_events); // p は uint8_t
    std::vector<uint64_t> t_data(num_events);
    std::vector<uint16_t> x_data(num_events);
    std::vector<uint16_t> y_data(num_events);

    // データ読み込み
    p_dataset.read(p_data.data(), PredType::NATIVE_UINT8);
    t_dataset.read(t_data.data(), PredType::NATIVE_UINT64);
    x_dataset.read(x_data.data(), PredType::NATIVE_UINT16);
    y_dataset.read(y_data.data(), PredType::NATIVE_UINT16);

    // イベントデータに変換
    std::vector<Event> events(num_events);
    for (size_t i = 0; i < num_events; ++i) {
        events[i].x = x_data[i];
        events[i].y = y_data[i];
        events[i].p = p_data[i];  // 極性を -1, 1 にする
        events[i].t = t_data[i];
    }

    return events;
}


// イベントデータからフレームを作成する関数
cv::Mat create_frame(const std::vector<Event>& events, int width, int height) {
    cv::Mat frame = cv::Mat(height, width, CV_8UC3, cv::Scalar(127, 127, 127)); // デフォルトは灰色
    for (const auto& event : events) {
        int clipped_x = std::clamp(static_cast<int>(event.x), 0, width - 1);
        int clipped_y = std::clamp(static_cast<int>(event.y), 0, height - 1);

        if (event.p == 1) {
            frame.at<cv::Vec3b>(clipped_y, clipped_x) = cv::Vec3b(0, 0, 0); // 黒
        } else if (event.p == 0) {
            frame.at<cv::Vec3b>(clipped_y, clipped_x) = cv::Vec3b(255, 255, 255); // 白
        }
    }
    return frame;
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <base_dir> <width> <height>" << std::endl;
        return 1;
    }

    std::string base_dir = argv[1];
    int width = std::stoi(argv[2]);
    int height = std::stoi(argv[3]);

    try {
        std::string hdf5_file;
        std::string trigger_file = join_path(base_dir, "image_offsets.txt");
        std::string events_dir = join_path(base_dir, "events");
        std::string output_dir = join_path(base_dir, "images/events");

        for (const auto& entry : std::filesystem::directory_iterator(events_dir)) {
            if (entry.path().extension() == ".h5") {
                hdf5_file = entry.path().string();
                break;
            }
        }

        if (hdf5_file.empty()) {
            throw std::runtime_error("No HDF5 file found in " + events_dir);
        }

        if (!std::filesystem::exists(output_dir)) {
            std::filesystem::create_directories(output_dir);
        }

        std::vector<int64_t> triggers = load_triggers(trigger_file);
        std::vector<Event> events = load_events_from_hdf5(hdf5_file);

        for (size_t i = 0; i < triggers.size(); ++i) {
            int64_t start_time = (i == 0) ? 0 : triggers[i - 1];
            int64_t end_time = triggers[i];

            std::vector<Event> filtered_events;
            std::copy_if(events.begin(), events.end(), std::back_inserter(filtered_events),
                         [start_time, end_time](const Event& e) {
                             return e.t >= start_time && e.t < end_time;
                         });

            cv::Mat frame = create_frame(filtered_events, width, height);

            std::ostringstream filename;
            filename << join_path(output_dir, "frame_") << std::setw(16) << std::setfill('0') << i << ".jpg";
            bool success = cv::imwrite(filename.str(), frame);
            if (!success) {
                std::cerr << "Failed to save frame: " << filename.str() << std::endl;
                continue;
            }
            std::cout << "Saved: " << filename.str() << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
