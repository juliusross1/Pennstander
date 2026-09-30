#!/usr/bin/env python3
"""Create a static PennstanderMath instance, including its MATH table.

fontTools 4.63.0 does not resolve PennstanderMath's MATH variation references
when creating a static instance. This script applies those adjustments before
fontTools instantiates the rest of the font.

Requires fontTools (tested with 4.63.0). From this directory:
    python3 instantiate_pennstander.py
    python3 instantiate_pennstander.py wght=700 MWGT=100 MLNT=50 -o Bold.ttf

Unspecified axes use the input font's named Regular instance. Axis overrides
are independent: changing wght does not automatically change MWGT or MLNT.
The output option changes the filename, not the font's internal family name.

Requires fonttools.  Written with ChatGPT.
"""

import argparse
import math
import os
from pathlib import Path
import tempfile

from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import Device, MathValueRecord
from fontTools.varLib.instancer import AxisLimits, instantiateVariableFont
from fontTools.varLib.varStore import VarStoreInstancer


def walk_tables(root):
    """Visit each object once, including shared MATH records."""
    seen = set()
    stack = [root]
    while stack:
        obj = stack.pop()
        if isinstance(obj, (str, bytes, int, float, type(None))):
            continue
        if id(obj) in seen:
            continue
        seen.add(id(obj))
        if isinstance(obj, (list, tuple)):
            stack.extend(obj)
        elif hasattr(obj, "__dict__"):
            yield obj
            stack.extend(vars(obj).values())


def regular_coordinates(font):
    if "fvar" not in font:
        raise ValueError("Input font is not variable (no fvar table).")
    for instance in font["fvar"].instances:
        names = [
            name.toUnicode().strip().casefold()
            for name in font["name"].names
            if name.nameID == instance.subfamilyNameID
        ]
        if "regular" in names:
            coords = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}
            coords.update(instance.coordinates)
            return coords
    raise ValueError("Input font has no named Regular instance.")


def instantiate_math(font, coordinates):
    """Bake this font's GDEF-backed MATH VariationIndex records into integers.

    Do this BEFORE ordinary instancing removes/remaps the GDEF variation store.
    Use the same normalization as the outline instancer, including avar v2.
    Ordinary pixel-size Device tables are preserved.
    """
    if "MATH" not in font:
        raise ValueError("Input font has no MATH table.")
    records = [
        obj for obj in walk_tables(font["MATH"].table)
        if isinstance(obj, MathValueRecord)
        and obj.DeviceTable is not None
        and obj.DeviceTable.DeltaFormat == 0x8000
    ]
    if not records:
        return 0
    store = getattr(font["GDEF"].table, "VarStore", None) if "GDEF" in font else None
    if store is None:
        raise ValueError("MATH has variation references but GDEF has no variation store.")
    limits = AxisLimits(coordinates).limitAxesAndPopulateDefaults(font)
    location = limits.normalize(font).pinnedLocation()
    instancer = VarStoreInstancer(store, font["fvar"].axes, location)
    for record in records:
        device = record.DeviceTable
        index = (device.StartSize << 16) | device.EndSize
        # 0xFFFFFFFF is the OpenType no-variation sentinel.
        if index != 0xFFFFFFFF:
            outer, inner = device.StartSize, device.EndSize
            if outer >= len(store.VarData) or inner >= store.VarData[outer].ItemCount:
                raise ValueError(f"MATH references an invalid variation index: {index:#x}")
        value = otRound(record.Value + instancer[index])
        if not -32768 <= value <= 32767:
            raise ValueError(f"Instantiated MATH value is outside int16 range: {value}")
        record.Value = value
        record.DeviceTable = None
    return len(records)


def validate_static_math(font):
    font.ensureDecompiled()
    if "fvar" in font or "gvar" in font or "avar" in font:
        raise ValueError("Output still contains variable-font tables.")
    if "MATH" not in font:
        raise ValueError("Output lost its MATH table.")
    for obj in walk_tables(font["MATH"].table):
        if isinstance(obj, Device) and obj.DeltaFormat == 0x8000:
            raise ValueError("Output MATH still contains an unresolved variation reference.")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("axes", nargs="*", metavar="TAG=VALUE",
                        help="Override a Regular coordinate; tags are case-sensitive.")
    parser.add_argument("-i", "--input", type=Path, default=Path("PennstanderMathVF.ttf"),
                        help="Input variable font (default: %(default)s).")
    parser.add_argument("-o", "--output", type=Path, default=Path("PennstanderMath.ttf"),
                        help="Output filename (default: %(default)s).")
    parser.add_argument("--overwrite", action="store_true",
                        help="Allow replacing an existing output file (default: refuse).")
    args = parser.parse_args()
    temporary = None
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must be different files.")
        if os.path.lexists(args.output) and not args.overwrite:
            raise ValueError(f"Output already exists: {args.output}. Use --overwrite to replace it.")
        with TTFont(args.input) as font:
            coordinates = regular_coordinates(font)
            axes = {axis.axisTag: axis for axis in font["fvar"].axes}
            supplied = set()
            for item in args.axes:
                tag, separator, raw = item.partition("=")
                if not separator or tag not in axes:
                    raise ValueError(f"Invalid axis assignment {item!r}; axes: {', '.join(axes)}")
                if tag in supplied:
                    raise ValueError(f"Axis {tag} was specified twice.")
                supplied.add(tag)
                value = float(raw)
                axis = axes[tag]
                if not math.isfinite(value) or not axis.minValue <= value <= axis.maxValue:
                    raise ValueError(f"{tag} must be between {axis.minValue:g} and {axis.maxValue:g}.")
                coordinates[tag] = value
            print("Coordinates: " + " ".join(f"{tag}={value:g}" for tag, value in coordinates.items()))
            count = instantiate_math(font, coordinates)
            instance = instantiateVariableFont(font, coordinates, inplace=True)
            validate_static_math(instance)
            # Validate a saved copy before replacing any existing output.
            with tempfile.NamedTemporaryFile(dir=args.output.parent, suffix=".ttf", delete=False) as tmp:
                temporary = Path(tmp.name)
            instance.save(temporary)
            with TTFont(temporary) as check:
                validate_static_math(check)
            if args.overwrite:
                os.replace(temporary, args.output)
                temporary = None
            else:
                # Atomically publish without replacing a file created during instancing.
                try:
                    os.link(temporary, args.output)
                except FileExistsError:
                    raise ValueError(
                        f"Output already exists: {args.output}. Use --overwrite to replace it."
                    ) from None
                temporary.unlink()
                temporary = None
        print(f"Resolved {count:,} MATH variation references.")
        print(f"Saved: {args.output}")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
