"""Compile the production staging block without a GPU; check retained construction work."""
import pathlib
import subprocess
import tempfile

source = pathlib.Path('MobileGlues-cpp/gl/multidraw.cpp').read_text()
start = source.index('static thread_local std::vector<draw_elements_indirect_command_t> staged;')
end = source.index('\n    for (GLsizei i', start)
block = source[start:end]
test = r'''
#include <vector>
#include <cstddef>
#include <cassert>
#include <cstdint>
static size_t constructed = 0;
struct draw_elements_indirect_command_t {
    uint32_t value;
    draw_elements_indirect_command_t() : value(0) { ++constructed; }
};
static uint64_t fill(int primcount) {
BLOCK
    uint64_t sum = 0;
    for (int i = 0; i < primcount; ++i) pcmds[i].value = i + 1;
    for (int i = 0; i < primcount; ++i) sum += pcmds[i].value;
    return sum;
}
int main() {
    assert(fill(8192) == 8192ULL * 8193 / 2);
    size_t warm = constructed;
    for (int n : {16, 4096, 1, 8192, 0, 512}) {
        assert(fill(n) == uint64_t(n) * (n + 1) / 2);
    }
    assert(constructed == warm && "oscillating counts rebuilt the overwritten tail");
    assert(fill(16384) == 16384ULL * 16385 / 2);
    size_t grown = constructed;
    assert(fill(2) == 3);
    assert(fill(16384) == 16384ULL * 16385 / 2);
    assert(constructed == grown);
}
'''.replace('BLOCK', block)
with tempfile.TemporaryDirectory() as tmp:
    cpp = pathlib.Path(tmp) / 'staging.cpp'
    cpp.write_text(test)
    binary = pathlib.Path(tmp) / 'staging'
    subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('PASS production staging: prefix checksums, oscillation, growth, zero draws')
