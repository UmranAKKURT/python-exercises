import zipfile
import argparse
import logging
import fnmatch
from pathlib import Path
from typing import List, Optional


def setup_logger(verbose: bool) -> None:
    """Loglama seviyesini ayarlar."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def is_excluded(path: Path, exclude_patterns: List[str]) -> bool:
    """Dosya yolunun hariç tutulan desenlerden biriyle eşleşip eşleşmediğini kontrol eder."""
    for pattern in exclude_patterns:
        # Hem dosya adında hem de tüm yolda eşleşme ara (Örn: *.log veya .git/*)
        if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(str(path), pattern):
            return True
    return False


def get_compression_method(algo_name: str) -> int:
    """String olarak verilen sıkıştırma türünü zipfile sabitlerine çevirir."""
    algorithms = {
        'deflate': zipfile.ZIP_DEFLATED,  # Standart hızlı sıkıştırma
        'bzip2': zipfile.ZIP_BZIP2,  # Daha iyi sıkıştırma, biraz daha yavaş
        'lzma': zipfile.ZIP_LZMA  # En iyi sıkıştırma, en yavaş
    }
    return algorithms.get(algo_name.lower(), zipfile.ZIP_DEFLATED)


def collect_files(target_path: Path, exclude_patterns: List[str]) -> List[Path]:
    """Sıkıştırılacak dosyaların filtrelenmiş listesini oluşturur."""
    files_to_zip = []

    if target_path.is_file():
        if not is_excluded(target_path, exclude_patterns):
            files_to_zip.append(target_path)
    elif target_path.is_dir():
        for path in target_path.rglob('*'):
            if path.is_file() and not is_excluded(path, exclude_patterns):
                files_to_zip.append(path)

    return files_to_zip


def create_archive(
        target_path: Path,
        output_path: Optional[Path],
        exclude_patterns: List[str],
        compression_algo: str,
        dry_run: bool
) -> None:
    # Çıktı yolu belirtilmediyse hedefin yanına .zip olarak oluştur
    if not output_path:
        output_path = target_path.with_name(f"{target_path.name}.zip")
    # Eğer çıktı yolu bir klasör olarak verildiyse, içine hedef adıyla zip oluştur
    elif output_path.is_dir():
        output_path = output_path / f"{target_path.name}.zip"

    # Sıkıştırılacak dosyaları topla
    logging.info("Sıkıştırılacak dosyalar taranıyor...")
    files_to_zip = collect_files(target_path, exclude_patterns)

    if not files_to_zip:
        logging.warning("Sıkıştırılacak uygun dosya bulunamadı! (Hepsi filtrelenmiş olabilir)")
        return

    # Kendi içine zip yapmayı önle (eğer zip dosyası hedef klasörün içine oluşturuluyorsa)
    files_to_zip = [f for f in files_to_zip if f.resolve() != output_path.resolve()]

    # Sadece test modu (dry-run) ise dosyaları listele ve çık
    if dry_run:
        logging.info(f"[SIMÜLASYON] {len(files_to_zip)} dosya '{output_path}' içine sıkıştırılacaktı.")
        for f in files_to_zip:
            logging.debug(f" -> {f}")
        return

    compression_method = get_compression_method(compression_algo)

    logging.info(f"Arşiv oluşturuluyor: {output_path} (Algoritma: {compression_algo.upper()})")

    with zipfile.ZipFile(output_path, 'w', compression=compression_method) as zip_file:
        for file_path in files_to_zip:
            # Zip içindeki hiyerarşiyi korumak için göreceli yol (relative path) hesapla
            if target_path.is_dir():
                arcname = file_path.relative_to(target_path.parent)
            else:
                arcname = file_path.name

            logging.debug(f"Ekleniyor: {arcname}")
            zip_file.write(file_path, arcname=arcname)

    logging.info(f"Başarılı! Toplam {len(files_to_zip)} dosya arşivlendi.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gelişmiş Dosya ve Klasör Sıkıştırma Aracı",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("hedef", type=str, help="Sıkıştırılacak kaynak dosya veya klasör")

    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Oluşturulacak ZIP dosyasının yolu veya adı")

    parser.add_argument("-e", "--exclude", type=str, nargs='+', default=[],
                        help="Hariç tutulacak dosya desenleri (Örn: *.log .git/* node_modules/*)")

    parser.add_argument("-c", "--compression", type=str, choices=['deflate', 'bzip2', 'lzma'],
                        default='deflate', help="Sıkıştırma algoritması")

    parser.add_argument("--dry-run", action="store_true",
                        help="İşlemi gerçekleştirmez, sadece hangi dosyaların işleneceğini gösterir")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="İşlem sırasındaki tüm detayları (eklenen dosyaları) gösterir")

    args = parser.parse_args()

    setup_logger(args.verbose)
    target_path = Path(args.hedef)

    if not target_path.exists():
        logging.error(f"Hedef bulunamadı: {target_path}")
        return

    try:
        output_path = Path(args.output) if args.output else None
        create_archive(
            target_path=target_path,
            output_path=output_path,
            exclude_patterns=args.exclude,
            compression_algo=args.compression,
            dry_run=args.dry_run
        )
    except PermissionError:
        logging.error("Dosyaları okumak/yazmak için gerekli izinlere sahip değilsiniz.")
    except Exception as e:
        logging.error(f"Kritik Hata: {e}")


if __name__ == "__main__":
    main()